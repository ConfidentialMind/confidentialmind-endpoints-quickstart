# Model Endpoint Examples

These examples demonstrate how to interact with our AI model endpoints, which use an OpenAI-compatible API interface. They cover various functionalities, including chat completions, streaming responses, and multimodal capabilities. The examples show integration with both HTTP requests and the OpenAI SDK.

## Model Endpoint vs Direct Model Deployment

ConfidentialMind offers two ways to deploy and access AI models:

### Model Endpoint
- **Multiple models**: One endpoint can serve multiple models dynamically
- **Stable connection details**: Add, remove, or update models without changing URL/API key
- **Explicit model selection**: Choose specific models by name in your requests
- **Trade-off**: Cannot use a single hard-coded model name while switching models

### Direct Model Deployment  
- **Single model**: One deployment serves one specific model (always appears as `cm-llm`)
- **Simple model reference**: Use `cm-llm` consistently regardless of the actual model
- **Dedicated resources**: Model has dedicated computational resources
- **Trade-off**: Requires new deployment (new URL/API key) to switch models

**Recommendation**: Model endpoints are generally preferred for their flexibility in model management and stable connection details.

## Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your API credentials:
   - **BASE_URL**: Your model endpoint or deployment URL  
   - **API_KEY**: Your API key from the ConfidentialMind portal
   - **MODEL_NAME**: Set to `cm-llm` for direct deployments, or use specific model names for model endpoints

## Examples

### List Available Models

Check what models are available at your endpoint:

- **List models**: `python list-models.py`

This example helps you understand whether you're connected to a model endpoint (multiple models) or a direct deployment (single `cm-llm` model).

### Basic Chat Completion

Two ways to interact with our chat completion API:

- **Using HTTP requests**: `python chat.py`
- **Using OpenAI SDK**: `python chat-openai-sdk.py`

### Streaming Chat Completion

Examples of streaming responses for real-time text generation:

- **Using HTTP requests**: `python chat-streaming.py`
- **Using OpenAI SDK**: `python chat-streaming-openai-sdk.py`

### Multimodal Capabilities

Process images with text instructions:

- **Basic image description**: `python multimodal.py`
- **Structured data extraction from images**: `python multimodal-json.py`

### Structured Data with Guided JSON

Get structured, schema-compliant responses:

- **Guided JSON output**: `python guided-json.py`

> **Note**: Our guided JSON capabilities have some limitations regarding schema complexity. For questions about advanced schema requirements or for assistance with structured output formats, please contact our support team.

## What's Happening?

These examples demonstrate how to:
- Set up authentication
- Send requests to our API endpoints
- Process and display responses

Our API mimics the OpenAI API interface, making integration seamless if you're already familiar with their SDK.

## Next Steps

For more advanced usage, please refer to our [detailed documentation](https://docs.confidentialmind.com).