# POE API to OpenAI API
This is a project that converts the official `poe.com` API to the OpenAI API. 

`poe-2-openai` `poe-to-openai` `poe-gpt-api` `poe-openai-api`  `poe-to-gpt` `poe-2-gpt` `poe-api` `gpt-api` `openai-api`

[简体中文说明](README_ZH.md)

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
