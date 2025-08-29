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
    model, messages, stream, tools, tool_choice = parse_request_body(body)
    if model is None:
        return JSONResponse(content={"error": "Invalid request body"}, status_code=400)

    token = await get_token_from_request(request)

    if stream:
        return StreamingResponse(process_openai_response_event_stream(model, messages, token, tools, tool_choice),
                                 media_type="text/event-stream")
    else:
        return await default_response(model, messages, token, tools, tool_choice)


def parse_request_body(body):
    try:
        model = body.get('model', 'gpt-3.5-turbo')
        messages = body.get('messages', [])
        stream = body.get('stream', False)
        tools = body.get('tools', None)
        tool_choice = body.get('tool_choice', None)
        
        return model, messages, stream, tools, tool_choice
    except json.JSONDecodeError as e:
        logger.debug(f"请求体解析错误: {e}")
        return None, None, None, None, None


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


async def process_openai_response_event_stream(model, messages, token, tools=None, tool_choice=None):
    async for result in poe_api.stream_get_responses(token, messages, model, tools, tool_choice):
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
            result_line = f"data: {json.dumps(web_response_to_api_response_stream(result.text, model))}\n\n"
            yield result_line
        elif result.data:
            # Handle JSON data responses
            result_line = f"data: {json.dumps(web_response_to_api_response_stream_json(result.data, model))}\n\n"
            yield result_line
    
    # 通知结束
    yield f"data: {json.dumps(web_response_to_api_response_stream('', model, True))}\n\n"
    # 通知结束
    yield "data: [DONE]\n\n"

def web_response_to_api_response_stream_tool_call(tool_call_data, model, stop=None):
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
        "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 100}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


def web_response_to_api_response_stream_json(data_json, model, stop=None):
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
        "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 100}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


def web_response_to_api_response_stream(result, model, stop=None):
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
        "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 100}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


async def default_response(model, messages, token, tools=None, tool_choice=None):
    result = await poe_api.get_responses(token, messages, model, tools, tool_choice)
    
    # Check if result contains tool calls
    if isinstance(result, dict) and result.get('tool_calls'):
        data = web_response_to_api_response_tool_call(model, result)
    else:
        data = web_response_to_api_response(model, result)
    
    return JSONResponse(content=data)


def web_response_to_api_response_tool_call(model, result):
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
        "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 100}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data


def web_response_to_api_response(model, result):
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
        "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 100}
    }

    logger.debug("openai 返回数据: %s", json.dumps(data, indent=2, ensure_ascii=False))

    return data
