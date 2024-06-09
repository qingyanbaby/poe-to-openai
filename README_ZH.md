# POE API to OpenAI API
这是一个`poe.com`官方API转openai的API的项目
仅支持接口`/v1/chat/completions`

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

### Docker COMPOSE运行

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

### 访问地址
```shell
# http://localhost:39527/v1/chat/completions
```

3.运行
```shell
docker compose up -d
```

## 模型转换说明
```python
model_mapping = {
    "gpt-3.5-turbo-16k": "ChatGPT-16k",
    "gpt-3.5-turbo": "ChatGPT",
    "gpt-4": "GPT-4",
    "gpt-4-turbo": "Claude-3-Opus",
    "gpt-4-vision-preview": "GPT-4-128k",
    "gpt-4-turbo-preview": "Claude-3-Opus-200k"
}
```