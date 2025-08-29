import requests
import json
import os

# 服务器地址
BASE_URL = "http://localhost:39527"
TOKEN = os.environ.get('CUSTOM_TOKEN', 'sk-qq669846')

def test_reasoning_mode():
    """测试reasoning模式功能"""
    print("测试reasoning模式功能...")
    
    # 测试请求数据
    test_data = {
        "max_completion_tokens": 32000,
        "max_reasoning_tokens": 10000,
        "max_tokens": 32000,
        "messages": [
            {"role": "user", "content": "Think carefully and solve: What is the next number in the sequence: 1, 1, 2, 3, 5, 8, 13, ?"}
        ],
        "model": "gpt-5",
        "reasoning_effort": "medium",
        "stream": False,
        "temperature": 1,
        "user": "hashed-da8acfc4bd0b70d03cf3b46ecbc2c583"
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", 
                               headers=headers, 
                               json=test_data)
        
        print(f"状态码: {response.status_code}")
        response_json = response.json()
        print("响应数据:")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        
        # 验证token计算
        if "usage" in response_json:
            usage = response_json["usage"]
            print(f"\nToken使用情况:")
            print(f"  提示token数: {usage.get('prompt_tokens', 0)}")
            print(f"  完成token数: {usage.get('completion_tokens', 0)}")
            print(f"  总token数: {usage.get('total_tokens', 0)}")
        
        return response_json
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def test_reasoning_mode_stream():
    """测试流式reasoning模式功能"""
    print("\n测试流式reasoning模式功能...")
    
    # 测试请求数据
    test_data = {
        "max_completion_tokens": 32000,
        "max_reasoning_tokens": 10000,
        "max_tokens": 32000,
        "messages": [
            {"role": "user", "content": "Think carefully and solve: What is the next number in the sequence: 1, 1, 2, 3, 5, 8, 13, ?"}
        ],
        "model": "gpt-5",
        "reasoning_effort": "medium",
        "stream": True,
        "temperature": 1,
        "user": "hashed-da8acfc4bd0b70d03cf3b46ecbc2c583"
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", 
                               headers=headers, 
                               json=test_data,
                               stream=True)
        
        print(f"状态码: {response.status_code}")
        print("流式响应数据:")
        
        final_usage = None
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)
                # 检查是否包含usage信息
                if "usage" in decoded_line and not "[DONE]" in decoded_line:
                    try:
                        # 提取usage信息
                        data_part = decoded_line.replace("data: ", "")
                        if data_part.strip():
                            chunk_data = json.loads(data_part)
                            if "usage" in chunk_data:
                                final_usage = chunk_data["usage"]
                    except:
                        pass
        
        # 显示最终的token使用情况
        if final_usage:
            print(f"\n最终Token使用情况:")
            print(f"  提示token数: {final_usage.get('prompt_tokens', 0)}")
            print(f"  完成token数: {final_usage.get('completion_tokens', 0)}")
            print(f"  总token数: {final_usage.get('total_tokens', 0)}")
                
    except Exception as e:
        print(f"请求失败: {e}")

def test_function_call_with_reasoning_mode():
    """测试带函数调用的reasoning模式"""
    print("\n测试带函数调用的reasoning模式...")
    
    # 测试请求数据
    test_data = {
        "max_completion_tokens": 32000,
        "max_reasoning_tokens": 10000,
        "max_tokens": 32000,
        "messages": [
            {"role": "user", "content": "What's the weather like in Beijing today? Think step by step."}
        ],
        "model": "gpt-5",
        "reasoning_effort": "high",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"]
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ],
        "tool_choice": "auto",
        "stream": False,
        "temperature": 1,
        "user": "hashed-da8acfc4bd0b70d03cf3b46ecbc2c583"
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", 
                               headers=headers, 
                               json=test_data)
        
        print(f"状态码: {response.status_code}")
        response_json = response.json()
        print("响应数据:")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        
        # 验证token计算
        if "usage" in response_json:
            usage = response_json["usage"]
            print(f"\nToken使用情况:")
            print(f"  提示token数: {usage.get('prompt_tokens', 0)}")
            print(f"  完成token数: {usage.get('completion_tokens', 0)}")
            print(f"  总token数: {usage.get('total_tokens', 0)}")
        
        return response_json
    except Exception as e:
        print(f"请求失败: {e}")
        return None

if __name__ == "__main__":
    print("Poe-to-OpenAI Reasoning Mode 测试脚本")
    print("=" * 50)
    
    # 测试普通reasoning模式
    test_reasoning_mode()
    
    # 测试流式reasoning模式
    test_reasoning_mode_stream()
    
    # 测试带函数调用的reasoning模式
    test_function_call_with_reasoning_mode()
    
    print("\n测试完成!")