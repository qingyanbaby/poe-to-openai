import logging

from fastapi import WebSocket, Form
from fastapi.responses import JSONResponse
from fastapi_poe.client import get_bot_response, get_final_response, QueryRequest
from fastapi_poe.types import ProtocolMessage

timeout = 120

logging.basicConfig(level=logging.DEBUG)

client_dict = {}

model_mapping = {
    "gpt-3.5-turbo-16k": "ChatGPT-16k",
    "gpt-3.5-turbo": "ChatGPT",
    "gpt-4": "GPT-4",
    "gpt-4-turbo": "Claude-3-Opus",
    "gpt-4-vision-preview": "GPT-4-128k",
    "gpt-4-turbo-preview": "Claude-3-Opus-200k"
}


async def get_responses(api_key, prompt=[], bot="gpt-4"):
    bot_name = get_bot(bot)
    # "system", "user", "bot"
    messages = openai_message_to_poe_message(prompt)
    print("=================", messages, "=================")

    additional_params = {"temperature": 0.7, "skip_system_prompt": True, "logit_bias": {}, "stop_sequences": []}
    query = QueryRequest(
        query=messages,
        user_id="",
        conversation_id="",
        message_id="",
        version="1.0",
        type="query",
        **additional_params
    )

    return await get_final_response(query, bot_name=bot_name, api_key=api_key)


async def stream_get_responses(api_key, prompt, bot):
    bot_name = get_bot(bot)
    messages = openai_message_to_poe_message(prompt)
    async for partial in get_bot_response(messages=messages, bot_name=bot_name, api_key=api_key,
                                          skip_system_prompt=False):
        yield partial.text


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


# @app.post("/add_token")
async def add_token_endpoint(token: str = Form(...)):
    return add_token(token)


# @app.post("/ask")
async def ask(token: str = Form(...), bot: str = Form(...), content: str = Form(...)):
    add_token(token)
    try:
        return await get_responses(token, content, bot)
    except Exception as e:
        errmsg = f"An exception of type {type(e).__name__} occurred. Arguments: {e.args}"
        logging.info(errmsg)
        return JSONResponse(status_code=400, content={"message": errmsg})


# @app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        token = await websocket.receive_text()
        bot = await websocket.receive_text()
        content = await websocket.receive_text()
        add_token(token)
        async for ret in stream_get_responses(token, content, bot):
            await websocket.send_text(ret)
    except Exception as e:
        errmsg = f"An exception of type {type(e).__name__} occurred. Arguments: {e.args}"
        logging.info(errmsg)
        await websocket.send_text(errmsg)
    finally:
        await websocket.close()


def get_bot(model):
    return model_mapping.get(model, "ChatGPT-16k")


def openai_message_to_poe_message(messages=[]):
    new_messages = []
    for message in messages:
        role = message["role"]
        if role == "assistant": role = "bot"
        new_messages.append(ProtocolMessage(role=role, content=message["content"]))

    return new_messages
