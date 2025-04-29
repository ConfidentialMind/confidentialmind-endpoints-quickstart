# Model Endpoint

The Model Endpoint provides an OpenAI-compatible API interface for accessing powerful language models. This system allows you to generate text responses based on conversation history, process both text and image inputs, create structured outputs in specific formats, and access multiple AI models through a unified interface.

## Base URL and Authentication

All requests to the Model endpoint must include:

1. **Base URL**: Your endpoint-specific base URL obtained from the portal
   ```bash
   https://api.example.com/v1/api/{endpoint-id}
   ```

2. **Authorization Header**: Your API key in the Authorization header
   ```bash
   Authorization: Bearer your-api-key-from-portal
   ```

## API Reference

### Chat Completions API

The Model Endpoint provides an OpenAI-compatible chat completions API that allows your applications to interact with language models.

```bash
POST {base_url}/chat/completions
```

**Headers:**
- `Authorization: Bearer your-api-key`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "model": "provider/model-name-variant",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.7,
  "max_tokens": 150,
  "stream": false
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | The full model identifier from the portal (e.g., "provider/model-name-variant") |
| `messages` | array | Yes | - | Array of messages in the conversation |
| `temperature` | number | No | 0.7 | Controls randomness (0-1) |
| `max_tokens` | integer | No | 150 | Maximum number of tokens to generate |
| `stream` | boolean | No | false | Whether to stream the response |
| `guided_json` | object | No | null | Structure definition for formatted JSON responses |

**Response (non-streaming):**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "provider/model-name-variant",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 10,
    "total_tokens": 35
  }
}
```

## Code Examples

### Basic Usage with OpenAI SDK

```python
from openai import OpenAI

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"
model_name = "provider/model-name-variant"  # Use full model ID from portal

# Initialize client
client = OpenAI(
    base_url=api_base_url,
    api_key=api_key
)

# Make a request
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].message.content)
```

### HTTP Request Method

```python
import requests

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"
model_name = "provider/model-name-variant"  # Use full model ID from portal

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.7,
    "max_tokens": 150
}

response = requests.post(
    f"{api_base_url}/chat/completions", 
    headers=headers,
    json=payload
)
result = response.json()

print("Model response:", result["choices"][0]["message"]["content"])
```

### Streaming Example

```python
import requests
import json

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"
model_name = "provider/model-name-variant"  # Use full model ID from portal

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.7,
    "stream": True
}

response = requests.post(
    f"{api_base_url}/chat/completions", 
    headers=headers,
    json=payload, 
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            chunk_data = line[6:]  # Remove 'data: ' prefix
            if chunk_data != '[DONE]':
                chunk = json.loads(chunk_data)
                content = chunk['choices'][0]['delta'].get('content', '')
                if content:
                    print(content, end='', flush=True)
```

### Multimodal Example

```python
from openai import OpenAI

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"
model_name = "provider/model-name-variant"  # Use full model ID from portal

# Initialize client
client = OpenAI(
    base_url=api_base_url,
    api_key=api_key
)

# Prepare a message with both text and image
message_content = [
    {"type": "text", "text": "What's in this image?"},
    {
        "type": "image_url",
        "image_url": {
            "url": "https://example.com/image.jpg"
        }
    }
]

# Make a request
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "user", "content": message_content}
    ],
    temperature=0.7,
    max_tokens=300
)

print(response.choices[0].message.content)
```

### Structured Output Example

```python
from openai import OpenAI

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"
model_name = "provider/model-name-variant"  # Use full model ID from portal

# Initialize client
client = OpenAI(
    base_url=api_base_url,
    api_key=api_key
)

# Define the structure for the output
guided_json = {
    "type": "object",
    "properties": {
        "city": {"type": "string"},
        "country": {"type": "string"},
        "population": {"type": "number"},
        "landmarks": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["city", "country", "landmarks"]
}

# Make a request
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "user", "content": "Tell me about Paris"}
    ],
    temperature=0.7,
    max_tokens=300,
    guided_json=guided_json
)

print(response.choices[0].message.content)
```

## Open WebUI Integration

You can connect your model endpoint to Open WebUI for a user-friendly chat interface:

```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL="https://api.example.com/v1/api/your-endpoint-id" \
  -e OPENAI_API_KEY="your-api-key-from-portal" \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

Then access Open WebUI at http://localhost:3000 and start chatting with your models.

## Finding Your Model ID

When making API requests, always use the full model identifier from the portal's Models section (e.g., "provider/model-name-variant"), not the display name (e.g., "Model Name"). The full model identifier is required for the API to correctly route your request to the appropriate model.

## Model Capabilities

The Model Endpoint provides several powerful capabilities:

1. **Text Generation**: Generate human-like text responses based on conversation context
2. **Multimodal Processing**: Process both text and image inputs for comprehensive understanding
3. **Structured Output**: Generate responses in specific formats using the guided_json parameter
4. **Model Variety**: Access different models for specialized use cases through the same API
5. **Streaming Responses**: Receive model outputs in real-time with streaming capability

## Best Practices

- Always use the full model identifier from the portal, not just the display name
- Use system messages to establish context and set expectations for the model
- For deterministic responses, set temperature to a lower value (0.0-0.3)
- For creative applications, use higher temperature settings (0.7-1.0)
- When requiring specific output formats, use the guided_json parameter
- Consider streaming responses for a more interactive user experience
- Optimize token usage by keeping prompts clear and concise