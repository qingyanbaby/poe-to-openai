import requests
import json

# 测试function call功能
def test_function_call():
    url = "http://localhost:39527/v1/chat/completions"
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-qq669846"  # 使用默认的自定义token
    }
    
    # 测试数据 - 包含工具定义
    data = {
        "model": "gpt-5",
        "messages": [
            {"role": "user", "content": "What's the weather like in Boston today?"}
        ],
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
        "tool_choice": "auto"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        
        # 测试流式响应
        print("\n=== 测试流式响应 ===")
        stream_data = {
            **data,
            "stream": True
        }
        stream_response = requests.post(url, headers=headers, json=stream_data, stream=True)
        print("Stream Status Code:", stream_response.status_code)
        for line in stream_response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_function_call()