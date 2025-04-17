# Model Endpoint Examples (TypeScript)

These examples demonstrate how to interact with our AI model endpoints using TypeScript. They cover various functionalities, including chat completions, streaming responses, and multimodal capabilities. The examples show integration with both HTTP requests (using Axios) and the OpenAI SDK.

## Setup

1. Install required packages:
   ```bash
   npm install
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your API credentials.

## Examples

### Basic Chat Completion

Two ways to interact with our chat completion API:

- **Using HTTP requests**: `npm run chat`
- **Using OpenAI SDK**: `npm run chat-openai-sdk`

### Streaming Chat Completion

Examples of streaming responses for real-time text generation:

- **Using HTTP requests**: `npm run chat-streaming`
- **Using OpenAI SDK**: `npm run chat-streaming-openai-sdk`

### Multimodal Capabilities

Process images with text instructions:

- **Basic image description**: `npm run multimodal`
- **Structured data extraction from images**: `npm run multimodal-json`

### Structured Data with Guided JSON

Get structured, schema-compliant responses:

- **Guided JSON output**: `npm run guided-json`

> **Note**: Our guided JSON capabilities have some limitations regarding schema complexity. For questions about advanced schema requirements or for assistance with structured output formats, please contact our support team.

## What's Happening?

These examples demonstrate how to:
- Set up authentication
- Send requests to our API endpoints
- Process and display responses

Our API mimics the OpenAI API interface, making integration seamless if you're already familiar with their SDK.

## Next Steps

For more advanced usage, please refer to our [detailed documentation](https://docs.confidentialmind.com).