# POE API to OpenAI API
这是一个`poe.com`官方API转openai的API的项目
仅支持接口`/v1/chat/completions`

## 更新日志
1.0.0  `/v1/chat/completions`接口支持

1.0.1  环境变量自定义模型映射

1.1.0  添加proxy支持

1.1.1  添加跨域配置

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

### 访问地址
```shell
# http://localhost:39527/v1/chat/completions
```

3.运行
```shell
docker compose build
docker compose up -d
```

## 模型转换说明
```shell
# 请在 .env 文件自定义编辑
MODEL_MAPPING='{
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-4o": "GPT-4o",
    "gpt-4-turbo": "GPT-4-Turbo"
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