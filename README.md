# POE API to OpenAI API
This is a project that converts the official `poe.com` API to the OpenAI API. 

`poe-2-openai` `poe-to-openai` `poe-gpt-api` `poe-openai-api`  `poe-to-gpt` `poe-2-gpt` `poe-api` `gpt-api` `openai-api`

[简体中文说明](README_ZH.md)

## Changelog
1.0.0  `/v1/chat/completions` endpoint support
1.0.1  Environment variable custom model mapping
1.1.0  Add proxy support

## Usage
### Running Locally

1. Clone the code to your local machine
```shell
git clone https://github.com/qingyanbaby/poe_2_openai.git
cd poe_2_openai
```

2. Obtain the POE API KEY
```shell
# Please go to https://poe.com/api_key to get your API KEY
# Then fill in the API KEY in the .env file
# CUSTOM_TOKEN=your_custom_token is used for accessing the API
# SYSTEM_TOKEN=your_poe_api_key is used for accessing the official POE API

cp .env.example .env
```

3. Install dependencies
```shell 
pip install -r requirements.txt
```

4. Run the application
```shell
python run.py
```

### Running with Docker Compose

1. Clone the code to your local machine 
```shell
git clone https://github.com/qingyanbaby/poe_2_openai.git
cd poe_2_openai
```

2. Obtain the POE API KEY
```shell
# Please go to https://poe.com/api_key to get your API KEY 
# Then fill in the API KEY in the docker-compose.yml file
# CUSTOM_TOKEN=your_custom_token is used for accessing the API
# SYSTEM_TOKEN=your_poe_api_key is used for accessing the official POE API
```

3. Run the application
```shell
docker compose build
docker compose up -d
```

### Access URL
```shell
# http://localhost:39527/v1/chat/completions
```

## Model Conversion Explanation
```shell
# edit the .env file
MODEL_MAPPING='{
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-4o": "GPT-4o",
    "gpt-4-turbo": "GPT-4-Turbo"
}'
```

## Proxy Settings
```shell
# Please customize and edit in the .env file
PROXY_TYPE=socks # socks/http, socks only supports socks5 proxy
PROXY_HOST=127.0.0.1 # Proxy address
PROXY_PORT=6668 # Proxy port
PROXY_USERNAME= # Proxy username, optional
PROXY_PASSWORD= # Proxy password, optional
```
