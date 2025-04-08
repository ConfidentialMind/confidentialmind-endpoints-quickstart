# OpenAI-Compatible Multi-Endpoint Proxy

## What is Open WebUI?

Open WebUI is a popular open-source ChatGPT-style interface for working with various AI models. It has a beautiful interface, conversation history, prompt library, and many other features that make it ideal for interacting with LLMs.

## Why a Proxy is Needed

When working with ConfidentialMind stack:
1. **Multiple Endpoints**: Different models in the stack have separate URLs and API keys
2. **OpenAI Compatibility**: Open WebUI expects an one single model endpoint
3. **Model Selection**: The proxy enables users to select any configured model from the Open WebUI dropdown menu

This proxy server creates an OpenAI-compatible endpoint that combines multiple models from your ConfidentialMind stack, making them all accessible through Open WebUI's interface.

## Overview

This proxy allows you to:
- Connect multiple LLM API endpoints under a single unified interface
- Present custom display names for models
- Route requests to appropriate backends based on model IDs
- Work seamlessly with OpenAI-compatible UIs like Open WebUI

## Features

- **Model Name Mapping**: Use friendly names for models while routing to actual backend names
- **API Key Management**: Securely store and use API keys for different endpoints
- **OpenAI API Compatibility**: Compatible with applications expecting the OpenAI API format
- **Streaming Support**: Properly handles both streaming and non-streaming responses
- **Dynamic Configuration**: Load model configurations from a JSON file
- **Health Check & Debugging**: Built-in endpoints for monitoring and troubleshooting

## Installation

### Prerequisites

- Python 3.7+
- Docker (optional, for containerized deployment)

### Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your endpoints in `config.json`:
   ```json
   {
     "endpoints": {
       "your-model-id": {
         "displayName": "Friendly Model Name",
         "url": "https://your-backend-api.com",
         "apiKey": "your-api-key",
         "actualModelName": "cm-llm"
       },
       "another-model-id": {
         "displayName": "Another Model",
         "url": "https://another-backend.com",
         "apiKey": "another-api-key",
         "actualModelName": "cm-llm"
       }
     }
   }
   ```

## Usage

### Running the Server

Start the proxy server:

```
python app.py
```

By default, the server runs on port 3333. You can change this by setting the `CM_OPEN_WEBUI_PROXY_PORT` environment variable:

```
CM_OPEN_WEBUI_PROXY_PORT=5000 python app.py
```

To specify a different configuration file:

```
CM_OPEN_WEBUI_PROXY_CONFIG_FILE=my-config.json python app.py
```

### Endpoints

- `GET /models`: List available models
- `POST /chat/completions`: Handle chat completions
- `GET /health`: Health check endpoint
- `GET /debug`: View current configuration (with masked API keys)
- `POST /reload`: Reload configuration file

All other OpenAI API endpoints are proxied through a generic handler.

### Using with Open WebUI

1. Start the proxy server:
   ```
   python app.py
   ```

2. Run Open WebUI with your proxy as the OpenAI API base URL:
   ```
   docker run -d -p 3000:8080 \
     --add-host=host.docker.internal:host-gateway \
     -e OPENAI_API_BASE_URL=http://host.docker.internal:3333 \
     -e OPENAI_API_KEY=asd \
     -v open-webui:/app/backend/data \
     --name open-webui \
     --restart always \
     ghcr.io/open-webui/open-webui:main
   ```

3. Access Open WebUI at http://localhost:3000 and select your configured models

## Configuration Details

Each model endpoint in the configuration requires the following fields:

- `displayName`: Human-readable name shown in UIs
- `url`: Base URL for the API endpoint
- `apiKey`: API key for authentication
- `actualModelName`: The model name expected by the backend service
