# POE API to OpenAI API
[简体中文说明](README_ZH.md)
This is a project that converts the official `poe.com` API to the OpenAI API. It only supports the `/v1/chat/completions` endpoint.

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
docker compose up -d
```

### Access URL
```shell
# http://localhost:39527/v1/chat/completions
```

## Model Conversion Explanation
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