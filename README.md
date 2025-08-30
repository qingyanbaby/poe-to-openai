# POE API to OpenAI API
This is a project that converts the official `poe.com` API to the OpenAI API. 

`poe-2-openai` `poe-to-openai` `poe-gpt-api` `poe-openai-api`  `poe-to-gpt` `poe-2-gpt` `poe-api` `gpt-api` `openai-api`

[简体中文说明](README_ZH.md)

## Changelog
1.0.0  `/v1/chat/completions` endpoint support

1.0.1  Environment variable custom model mapping

1.1.0  Add proxy support

1.1.1  Add cross-origin configuration

1.2.0  Add image generation support (`/v1/images/generations`)

1.3.0  Add function calling support

1.4.0  Add reasoning mode support

1.5.0  Add claude-code-router calling support with complex tool schema compatibility

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
# Chat completions:
http://localhost:39527/v1/chat/completions

# Image generation:
http://localhost:39527/v1/images/generations
```

## API Endpoints

### 1. Chat Completions
Endpoint: `/v1/chat/completions`

Example request:
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "Hello"}
  ]
}
```

#### Function Calling Example:
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "What's the weather like in Beijing?"}
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

#### Reasoning Mode Example:
```json
{
  "model": "gpt-5",
  "messages": [
    {"role": "user", "content": "Think carefully and solve: What is the next number in the sequence: 1, 1, 2, 3, 5, 8, 13, ?"}
  ],
  "reasoning_effort": "high",
  "max_reasoning_tokens": 10000,
  "max_completion_tokens": 32000
}
```

### 2. Claude-Code-Router Support
Endpoint: `/v1/chat/completions`

This version supports complex tool schemas from claude-code-router, including:
- Complex `allOf` JSON Schema structures
- Composite types like `["boolean", "string"]`
- Advanced parameter constraints and validations

Example request with complex tools:
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "Fetch content from https://example.com with image processing"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "mcp__fetch__imageFetch",
        "description": "Retrieves URLs from the Internet and extracts their content as markdown with image processing support",
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

### 3. Image Generation
Endpoint: `/v1/images/generations` 

Example request:
```json
{
  "model": "dall-e-3",
  "prompt": "A beautiful sunset over the mountains",
  "n": 1, // only support n=1
  "size": "1024x1024"
}
```

## Model Conversion Explanation
```shell
# edit the .env file
MODEL_MAPPING='{
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-4o": "GPT-4o",
    "gpt-4-turbo": "GPT-4-Turbo",
    "dall-e-3": "DALL-E-3",
    "dall-e-2": "DALL-E-2",
    "midjourney": "Midjourney"
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