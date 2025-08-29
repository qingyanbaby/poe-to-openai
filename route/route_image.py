import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api import poe_api
from util import utils

logger = logging.getLogger(__name__)

router = APIRouter()
load_dotenv()


@router.post("/v1/images/generations")
async def image_generation(request: Request):
    """
    兼容OpenAI的图像生成API
    """
    body = await request.json()
    prompt, n, size, model, response_format = parse_request_body(body)
    
    token = await get_token_from_request(request)
    
    # 处理提示词和尺寸
    formatted_prompt = format_prompt_with_size(prompt, size)
    
    result = await generate_image(token, formatted_prompt, model)
    
    return JSONResponse(content=format_response(result, n, size, prompt))


def parse_request_body(body):
    """
    解析请求体，提取参数
    """
    try:
        prompt = body.get('prompt', '')
        n = body.get('n', 1)  # OpenAI支持生成多张图片，但Poe目前一次只能生成一张
        size = body.get('size', '1024x1024')  # OpenAI格式的尺寸
        model = body.get('model', 'dall-e-3')  # 默认使用DALL-E-3
        response_format = body.get('response_format', 'url')  # url或b64_json
            
        return prompt, n, size, model, response_format
    except Exception as e:
        logger.error(f"解析请求体错误: {e}")
        return None, 1, '1024x1024', "dall-e-3", "url"


def format_prompt_with_size(prompt, size):
    """
    根据OpenAI的尺寸参数格式化提示词，转换为aspect比例
    """
    # 如果用户在prompt中已经指定了尺寸或宽高比，不再添加
    if "--size" in prompt or "--aspect" in prompt:
        return prompt
        
    # 将OpenAI的尺寸格式转换为宽高比
    try:
        if 'x' in size:
            width, height = map(int, size.split('x'))
            aspect_ratio = f"{width}:{height}"
            return f"{prompt} --aspect 1:1"
        else:
            # 如果不是标准尺寸格式，直接返回原始提示词
            return prompt
    except Exception:
        # 解析失败时返回原始提示词
        return prompt


async def get_token_from_request(request_data):
    """
    从请求头中获取token
    """
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


async def generate_image(token, prompt, model="dall-e-3"):
    """
    调用Poe API生成图片
    """
    # 使用poe_api生成图片并获取结果
    result = await poe_api.get_image(token, prompt, model)
    return result


def format_response(result, n=1, size="1024x1024", prompt=""):
    """
    将Poe的响应格式化为OpenAI格式
    """
    # 分析result，提取图片URL
    # 假设result包含Markdown格式的图片链接，如: ![描述](URL)
    image_url = extract_image_url(result)
    
    current_time = int(datetime.now().timestamp())
    
    data = {
        "created": current_time,
        "data": [
            {
                "url": image_url,
                "revised_prompt": prompt
            }
        ]
    }
    
    logger.debug("图片生成响应: %s", json.dumps(data, indent=2, ensure_ascii=False))
    
    return data


def extract_image_url(result):
    """
    从Markdown格式的结果中提取图片URL
    """
    # 假设格式为 ![描述](URL)
    try:
        # 简单的解析方法，寻找第一个 '](' 和 ')' 之间的内容
        if '![](' in result or '![' in result and '](' in result:
            start_index = result.find('](') + 2
            end_index = result.find(')', start_index)
            if start_index > 1 and end_index > start_index:
                return result[start_index:end_index]
        
        # 如果上面的解析失败，可能是直接返回了URL
        return result.strip()
    except Exception as e:
        logger.error(f"提取图片URL失败: {e}")
        return result  # 返回原始结果 