# Model Endpoint Examples

These examples demonstrate how to interact with our AI model endpoints, which use an OpenAI-compatible API interface.

## Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your API credentials.

## Examples

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

For more advanced usage, please refer to our [detailed documentation](https://docs.confidentialmind.com/).