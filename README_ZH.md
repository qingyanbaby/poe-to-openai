# POE API to OpenAI API
这是一个`poe.com`官方API转openai的API的项目
支持接口`/v1/chat/completions`和`/v1/images/generations`

## 更新日志
1.0.0  `/v1/chat/completions`接口支持

1.0.1  环境变量自定义模型映射

1.1.0  添加proxy支持

1.1.1  添加跨域配置

1.2.0  添加图像生成支持 (`/v1/images/generations`)

1.3.0  添加函数调用支持

1.4.0  添加推理模式支持

1.5.0  添加claude-code-router调用支持，兼容复杂工具Schema

## 使用方式
### 本地运行

1. 拉去代码到本地
```shell
git clone https://github.com/qingyanbaby/poe_2_openai.git
cd poe_2_openai
```

2. 获取poe的API KEY
```shell
# 请到 https://poe.com/api_key 获取API KEY
# 然后将API KEY填写到 .env 文件中
# CUSTOM_TOKEN=your_custom_token 用于接口访问的token
# SYSTEM_TOKEN=your_poe_api_key 用于访问poe官方API的token

cp .env.example .env
```

3. 安装依赖
```shell
pip install -r requirements.txt
```

4. 运行
```shell
python run.py
```

### Docker Compose运行

1. 拉去代码到本地
```shell
git clone https://github.com/qingyanbaby/poe_2_openai.git
cd poe_2_openai
```

2. 获取poe的API KEY
```shell
# 请到 https://poe.com/api_key 获取API KEY
# 然后将API KEY填写到 docker-compose.yml 文件中
# CUSTOM_TOKEN=your_custom_token 用于接口访问的token
# SYSTEM_TOKEN=your_poe_api_key 用于访问poe官方API的token
```

3.运行
```shell
docker compose build
docker compose up -d
```

### 访问地址
```shell
# 聊天接口:
http://localhost:39527/v1/chat/completions

# 图像生成接口:
http://localhost:39527/v1/images/generations
```

## API 接口

### 1. 聊天接口
接口地址: `/v1/chat/completions`

请求示例:
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}
```

#### 函数调用示例:
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "北京的天气怎么样？"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "description": "获取指定位置的当前天气",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "城市和省份，例如：北京"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

#### 推理模式示例:
```json
{
  "model": "gpt-5",
  "messages": [
    {"role": "user", "content": "仔细思考并解决：数列 1, 1, 2, 3, 5, 8, 13, ? 的下一个数字是什么？"}
  ],
  "reasoning_effort": "high",
  "max_reasoning_tokens": 10000,
  "max_completion_tokens": 32000
}
```

### 2. Claude-Code-Router支持
接口地址: `/v1/chat/completions`

此版本支持claude-code-router的复杂工具Schema，包括：
- 复杂的`allOf` JSON Schema结构
- 复合类型如`["boolean", "string"]`
- 高级参数约束和验证

复杂工具调用示例:
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "从https://example.com获取内容并处理图像"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "mcp__fetch__imageFetch",
        "description": "从互联网获取URL内容并提取为markdown格式，支持图像处理",
        "parameters": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            },
            "enableFetchImages": {
              "type": ["boolean", "string"],
              "default": false
            },
            "imageMaxCount": {
              "allOf": [
                {"type": ["number", "string"]},
                {"type": "number", "minimum": 0, "maximum": 10}
              ],
              "default": 3
            }
          },
          "required": ["url"]
        }
      }
    }
  ]
}
```

### 3. 图像生成接口
接口地址: `/v1/images/generations`

请求示例:
```json
{
  "model": "dall-e-3",
  "prompt": "一只可爱的小猫",
  "n": 1, // 只支持n=1
  "size": "1024x1024"
}
```

## 模型转换说明
```shell
# 请在 .env 文件自定义编辑
MODEL_MAPPING='{
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-4o": "GPT-4o",
    "gpt-4-turbo": "GPT-4-Turbo",
    "dall-e-3": "DALL-E-3",
    "flux-dev": "FLUX-dev"
}'
```

## 代理设置
```shell
# 请在 .env 文件自定义编辑
PROXY_TYPE=socks # socks/http，socks仅支持socks5代理
PROXY_HOST=127.0.0.1 # 代理地址
PROXY_PORT=6668 # 代理端口
PROXY_USERNAME= # 代理用户名，可选
PROXY_PASSWORD= # 代理密码，可选
```