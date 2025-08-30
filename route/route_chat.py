import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from api import poe_api
from util import utils
from util.token_utils import calculate_usage

app = FastAPI()
logger = logging.getLogger(__name__)

router = APIRouter()
load_dotenv()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/v1/chat/completions")
async def chat_proxy(request: Request):
    body = await request.json()
    model, messages, stream, tools, tool_choice, reasoning_effort, max_reasoning_tokens, max_completion_tokens = parse_request_body(body)
    if model is None:
        return JSONResponse(content={"error": "Invalid request body"}, status_code=400)

    # 预处理消息，添加 reasoning 参数标记
    processed_messages = preprocess_last_user_message(messages, reasoning_effort, max_reasoning_tokens)

    token = await get_token_from_request(request)

    if stream:
        return StreamingResponse(process_openai_response_event_stream(model, processed_messages, token, tools, tool_choice, reasoning_effort, max_reasoning_tokens, max_completion_tokens),
                                 media_type="text/event-stream")
    else:
        return await default_response(model, processed_messages, token, tools, tool_choice, reasoning_effort, max_reasoning_tokens, max_completion_tokens)


def parse_request_body(body):
    try:
        model = body.get('model', 'gpt-3.5-turbo')
        messages = body.get('messages', [])
        stream = body.get('stream', False)
        tools = body.get('tools', None)
        tool_choice = body.get('tool_choice', None)
        
        # Parse reasoning mode parameters
        reasoning_effort = body.get('reasoning_effort', None)
        max_reasoning_tokens = body.get('max_reasoning_tokens', None)
        max_completion_tokens = body.get('max_completion_tokens', None)
        
        return model, messages, stream, tools, tool_choice, reasoning_effort, max_reasoning_tokens, max_completion_tokens
    except json.JSONDecodeError as e:
        logger.debug(f"请求体解析错误: {e}")
        return None, None, None, None, None, None, None, None


def preprocess_last_user_message(messages, reasoning_effort=None, max_reasoning_tokens=None):
    """预处理最后一条用户消息，添加 reasoning 参数标记"""
    if not messages:
        return messages
    
    # 创建消息副本以避免修改原始列表
    processed_messages = [msg.copy() for msg in messages]
    
    # 获取最后一条消息
    last_message = processed_messages[-1]
    
    # 检查是否为用户消息且内容为字符串
    if last_message.get("role") == "user" and isinstance(last_message.get("content"), str):
        content = last_message["content"]
        
        # 检查是否已包含标记
        has_reasoning_effort = "--reasoning_effort=" in content
        has_thinking_budget = "--thinking_budget=" in content
        
        # 构建要追加的标记
        append_parts = []
        
        # 处理 reasoning_effort
        if reasoning_effort and reasoning_effort in ["minimal", "low", "medium", "high"] and not has_reasoning_effort:
            append_parts.append(f" --reasoning_effort={reasoning_effort}")
        
        # 处理 max_reasoning_tokens
        if max_reasoning_tokens is not None and not has_thinking_budget:
            try:
                budget = int(max_reasoning_tokens)
                # 裁剪范围到 0-30768
                budget = max(0, min(budget, 30768))
                append_parts.append(f" --thinking_budget={budget}")
            except (ValueError, TypeError):
                pass  # 忽略无效值
        
        # 如果有要追加的内容，则追加到消息末尾
        if append_parts:
            # 去除尾部空格后再追加
            content = content.rstrip()
            content += "".join(append_parts)
            last_message["content"] = content
    
    return processed_messages


async def get_token_from_request(request_data):
    logger.info("请求头: %s", request_data.headers)
    logger.info("开始获取token")
    token = request_data.headers.get('Authorization', '').replace('Bearer ', '')

    # 自定义token
    custom_token = os.environ.get('CUSTOM_TOKEN')
    # 内置token
    system_token = os.environ.get('SYSTEM_TOKEN')

    if token == custom_token:
        return system_token

    return token


async def process_openai_response_event_stream(model, messages, token, tools=None, tool_choice=None, reasoning_effort=None, max_reasoning_tokens=None, max_completion_tokens=None):
    # Collect all text chunks to calculate usage
    text_chunks = []
    
    async for result in poe_api.stream_get_responses(token, messages, model, tools, tool_choice, reasoning_effort, max_reasoning_tokens, max_completion_tokens):
        # Check if result has tool calls
        if hasattr(result, 'tool_calls') and result.tool_calls:
            # Handle tool calls in streaming response
            for tool_call in result.tool_calls:
                tool_call_data = {
                    "index": getattr(tool_call, 'index', 0),
                    "id": getattr(tool_call, 'id', None),
                    "type": getattr(tool_call, 'type', 'function'),
                    "function": {
                        "name": getattr(tool_call.function, 'name', ''),
                        "arguments": getattr(tool_call.function, 'arguments', '')
                    }
                }
                result_line = f"data: {json.dumps(web_response_to_api_response_stream_tool_call(tool_call_data, model))}\n\n"
                yield result_line
        elif hasattr(result, 'text') and result.text:
            text_chunks.append(result.text)
            result_line = f"data: {json.dumps(web_response_to_api_response_stream(result.text, model))}\n\n"
            yield result_line
        elif result.data:
            # Handle JSON data responses
            result_line = f"data: {json.dumps(web_response_to_api_response_stream_json(result.data, model))}\n\n"
            yield result_line
    
    # Calculate and yield final usage
    prompt_text = "\n".join([msg.get("content", "") for msg in messages])
    completion_text = "".join(text_chunks)
    usage = calculate_usage(prompt_text, completion_text, model)
    
    # 通知结束
    yield f"data: {json.dumps(web_response_to_api_response_stream('', model, True, usage))}\n\n"
    # 通知结束
    yield "data: [DONE]\n\n"

def web_response_to_api_response_stream_tool_call(tool_call_data, model, stop=None, usage=None):
    data = {
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "system_fingerprint": f"fp_{utils.get_8_random_str()}",
        "choices": [{
            "index": 0,
            "delta": {
                "tool_calls": [tool_call_data]
            },
            "finish_reason": "tool_calls" if not stop else "stop"
        }],
        "usage": usage if usage else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


def web_response_to_api_response_stream_json(data_json, model, stop=None, usage=None):
    data = {
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "system_fingerprint": f"fp_{utils.get_8_random_str()}",
        "choices": [{
            "index": 0,
            "delta": data_json,
            "finish_reason": "stop" if stop else None
        }],
        "usage": usage if usage else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


def web_response_to_api_response_stream(result, model, stop=None, usage=None):
    data = {
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "system_fingerprint": f"fp_{utils.get_8_random_str()}",
        "choices": [{
            "index": 0,
            "delta": {"content": f"{result}"},
            "finish_reason": "stop" if stop else None
        }],
        "usage": usage if usage else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


async def default_response(model, messages, token, tools=None, tool_choice=None, reasoning_effort=None, max_reasoning_tokens=None, max_completion_tokens=None):
    result = await poe_api.get_responses(token, messages, model, tools, tool_choice, reasoning_effort, max_reasoning_tokens, max_completion_tokens)
    
    # Calculate usage
    prompt_text = "\n".join([msg.get("content", "") for msg in messages])
    completion_text = result.get('text', '') if isinstance(result, dict) else str(result)
    usage = calculate_usage(prompt_text, completion_text, model)
    
    # Check if result contains tool calls
    if isinstance(result, dict) and result.get('tool_calls'):
        data = web_response_to_api_response_tool_call(model, result, usage)
    else:
        data = web_response_to_api_response(model, result, usage)
    
    return JSONResponse(content=data)


def web_response_to_api_response_tool_call(model, result, usage=None):
    data = {
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "system_fingerprint": f"fp_{utils.get_8_random_str()}",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": result['tool_calls']
            },
            "logprobs": None,
            "finish_reason": "tool_calls"
        }],
        "usage": usage if usage else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


def web_response_to_api_response(model, result, usage=None):
    # Extract text from result
    if isinstance(result, dict):
        content = result.get('text', '')
    else:
        content = str(result)
        
    data = {
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "system_fingerprint": f"fp_{utils.get_8_random_str()}",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "logprobs": None,
            "finish_reason": "stop"
        }],
        "usage": usage if usage else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data
