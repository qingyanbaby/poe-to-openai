import json
import logging
import os

import httpx
from fastapi import Form
from fastapi.responses import JSONResponse
from fastapi_poe import stream_request, get_final_response, QueryRequest, ToolDefinition, ToolCallDefinition, ToolResultDefinition, ProtocolMessage

timeout = 120

logging.basicConfig(level=logging.DEBUG)

client_dict = {}


async def get_responses(api_key, prompt=[], bot="gpt-4", tools=None, tool_choice=None):
    bot_name = get_bot(bot)
    # "system", "user", "bot"
    messages = openai_message_to_poe_message(prompt)
    print("=================", messages, "=================")

    additional_params = {"temperature": 0.7, "skip_system_prompt": False, "logit_bias": {}, "stop_sequences": []}
    query = QueryRequest(
        query=messages,
        user_id="",
        conversation_id="",
        message_id="",
        version="1.0",
        type="query",
        **additional_params
    )

    session = create_client()
    
    # Convert OpenAI tools to POE ToolDefinition
    poe_tools = None
    if tools:
        poe_tools = [convert_openai_tool_to_poe_tool(tool) for tool in tools]
    
    # Use stream_request and collect all responses
    chunks = []
    tool_calls_data = []
    tool_calls_dict = {}  # To collect and merge tool call chunks
    
    async for message in stream_request(
        request=query,
        bot_name=bot_name,
        api_key=api_key,
        tools=poe_tools,
        tool_executables=None,
        session=session
    ):
        # Collect text chunks
        if hasattr(message, 'text') and message.text:
            chunks.append(message.text)
        
        # Check for tool calls directly in message
        if hasattr(message, 'tool_calls') and message.tool_calls:
            # Collect all tool call chunks
            for tool_call_delta in message.tool_calls:
                if tool_call_delta.index is not None:
                    index = tool_call_delta.index
                    # Initialize or get existing tool call data
                    if index not in tool_calls_dict:
                        tool_calls_dict[index] = {
                            'index': index,
                            'id': None,
                            'type': None,
                            'function': {
                                'name': None,
                                'arguments': ''
                            }
                        }
                    
                    # Merge the delta data
                    if tool_call_delta.id is not None:
                        tool_calls_dict[index]['id'] = tool_call_delta.id
                    if tool_call_delta.type is not None:
                        tool_calls_dict[index]['type'] = tool_call_delta.type
                    if tool_call_delta.function.name is not None:
                        tool_calls_dict[index]['function']['name'] = tool_call_delta.function.name
                    if tool_call_delta.function.arguments is not None:
                        tool_calls_dict[index]['function']['arguments'] += tool_call_delta.function.arguments
    
    # Convert collected tool calls to the final format
    if tool_calls_dict:
        # Sort by index and convert to list
        sorted_tool_calls = [tool_calls_dict[i] for i in sorted(tool_calls_dict.keys())]
        tool_calls_data = sorted_tool_calls
    
    # Return an object with both text and tool_calls
    result = {
        'text': "".join(chunks),
        'tool_calls': tool_calls_data if tool_calls_data else None
    }
    return result


async def stream_get_responses(api_key, prompt, bot, tools=None, tool_choice=None):
    bot_name = get_bot(bot)
    messages = openai_message_to_poe_message(prompt)

    additional_params = {"temperature": 0.7, "skip_system_prompt": False, "logit_bias": {}, "stop_sequences": []}
    query = QueryRequest(
        query=messages,
        user_id="",
        conversation_id="",
        message_id="",
        version="1.0",
        type="query",
        **additional_params
    )

    session = create_client()
    
    # Convert OpenAI tools to POE ToolDefinition
    poe_tools = None
    if tools:
        poe_tools = [convert_openai_tool_to_poe_tool(tool) for tool in tools]
    
    async for partial in stream_request(
        request=query,
        bot_name=bot_name,
        api_key=api_key,
        tools=poe_tools,
        tool_executables=None,
        session=session
    ):
        yield partial


async def get_image(api_key, prompt, bot="dall-e-3"):
    """
    使用Poe API生成图像
    
    Args:
        api_key: Poe API密钥
        prompt: 图像生成提示词
        bot: 要使用的图像生成机器人名称
        
    Returns:
        生成的图像URL
    """
    bot_name = get_bot(bot)
    message = ProtocolMessage(role="user", content=prompt)
    
    session = create_client()
    logging.info(f"发送图像生成请求到 {bot_name}，提示词: {prompt}")
    
    result = ""
    async for partial in get_bot_response(messages=[message], bot_name=bot_name, api_key=api_key,
                                          skip_system_prompt=False, session=session):
        # 保存最终结果
        if partial.text and (partial.text.startswith("![") or "http" in partial.text):
            result = partial.text
            logging.info(f"收到图像结果: {result}")
    
    return result


def add_token(token: str):
    if token not in client_dict:
        try:
            client_dict[token] = token
            return "ok"
        except Exception as exception:
            logging.info("Failed to connect to poe due to " + str(exception))
            return "failed: " + str(exception)
    else:
        return "exist"


def get_bot(model):
    model_mapping = json.loads(os.environ.get("MODEL_MAPPING", "{}"))
    return model_mapping.get(model, "GPT-4o")


def openai_message_to_poe_message(messages=[]):
    new_messages = []
    for message in messages:
        role = message["role"]
        if role == 'developer':
            continue
        if role == "assistant":
            role = "bot"
        if role == "tool":
            role = "tool"

        # Handle content properly based on its type
        content = message["content"]
        if isinstance(content, list):
            # Process the list of content parts
            processed_content = ""
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        processed_content += item.get("text", "")
                    # Handle other types as needed
                else:
                    processed_content += str(item)
            content = processed_content
        elif not isinstance(content, str):
            content = str(content)

        new_messages.append(ProtocolMessage(role=role, content=content))
    return new_messages

def create_client():
    proxy_config = {
        "proxy_type": os.environ.get("PROXY_TYPE"),
        "proxy_host": os.environ.get("PROXY_HOST"),
        "proxy_port": os.environ.get("PROXY_PORT"),
        "proxy_username": os.environ.get("PROXY_USERNAME"),
        "proxy_password": os.environ.get("PROXY_PASSWORD"),
    }

    proxy = create_proxy(proxy_config)
    if proxy:
        client = httpx.AsyncClient(timeout=600, proxy=proxy)
    else:
        client = httpx.AsyncClient(timeout=600)
    return client


def create_proxy(proxy_config):
    proxy_type = proxy_config["proxy_type"]
    proxy_url = create_proxy_url(proxy_config)

    if proxy_type in ["http", "socks"] and proxy_url:
        return {
            "http://": proxy_url,
            "https://": proxy_url,
        }
    else:
        return None


def create_proxy_url(proxy_config):
    proxy_type = proxy_config["proxy_type"]
    proxy_host = proxy_config["proxy_host"]
    proxy_port = proxy_config["proxy_port"]
    proxy_username = proxy_config["proxy_username"]
    proxy_password = proxy_config["proxy_password"]

    if not proxy_host or not proxy_port:
        return None

    if proxy_type == "http":
        return f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    elif proxy_type == "socks":
        return f"socks5://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    else:
        return None


def convert_openai_tool_to_poe_tool(tool):
    """Convert OpenAI tool format to POE ToolDefinition"""
    if "function" in tool:
        function = tool["function"]
        return ToolDefinition(
            type="function",
            function=ToolDefinition.FunctionDefinition(
                name=function.get("name", ""),
                description=function.get("description", ""),
                parameters=ToolDefinition.FunctionDefinition.ParametersDefinition(
                    type="object",
                    properties=function.get("parameters", {}).get("properties", {}),
                    required=function.get("parameters", {}).get("required", [])
                )
            )
        )
    return None
