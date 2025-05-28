# Connecting Open WebUI to ConfidentialMind Models

This guide shows how to connect Open WebUI to models running in the ConfidentialMind stack. Open WebUI is a popular open-source ChatGPT-style interface with conversation history, prompt library, and many other features that make it ideal for interacting with LLMs.

## Prerequisites

- Docker installed on your machine (or other equivalent, like podman)
- Model running in the ConfidentialMind stack
- URL and API key for your model deployment or model endpoint

## Quick Start

### Option 1: Using Environment Variables (Recommended for Model Endpoints)

This approach works especially well with model endpoints as you can change/add/remove models while the URL and API key stay the same.

```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL="https://your-model-endpoint-url/v1" \
  -e OPENAI_API_KEY="your-api-key" \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

Replace:
- `https://your-model-endpoint-url/v1` with your model endpoint URL (note the `/v1` suffix)
- `your-api-key` with your API key from the ConfidentialMind portal

### Option 2: Manual UI Setup

1. **Run Open WebUI:**
   ```bash
   docker run -d -p 3000:8080 \
     -v open-webui:/app/backend/data \
     --name open-webui \
     --restart always \
     ghcr.io/open-webui/open-webui:main
   ```

2. **Configure connection in UI:**
   - Open http://localhost:3000/ in your browser
   - Create an admin account (use any values for local deployment)
   - Go to Settings → Connections → Click "+" in "Manage Direct Connections"
   - Paste your model's URL and add `/v1` to the end
   - Add your model's API key
   - Add model ID: `cm-llm`
   - Click save

3. **Test the connection:**
   - Go to main view and refresh
   - Select `cm-llm` as model at the top if needed
   - Send a test message

## Model Endpoints vs Single Model Deployments

- **Model Endpoint**: Supports multiple models dynamically. Use this for flexibility and easier management.
- **Single Model Deployment**: One specific model per deployment. The model will appear as `cm-llm` in Open WebUI.

For model endpoints, you can see all available models in the dropdown once connected. For single deployments, only `cm-llm` will be available.

## RAG Integration with Open WebUI Functions

You can add RAG (Retrieval-Augmented Generation) capabilities to Open WebUI using a custom Function that automatically retrieves relevant context before querying the LLM.

### Setup RAG Function

1. **Enable Functions in Open WebUI:**
   - Go to Settings → Functions
   - Enable "Allow Functions"

2. **Add the RAG Context Filter Function:**
   - Click "+" to create a new function
   - Copy and paste the function code from `rag-context-filter.py`
   - Save the function

3. **Configure the Function:**
   - Click the gear icon next to the RAG function
   - Set your RAG endpoint URL (e.g., `http://localhost:8000`)
   - Set your RAG API key
   - Configure other settings as needed (max_chunks, filters, etc.)
   - Set as a global function for it to work across all models

### Using RAG with Open WebUI

1. **Select a regular model** (not RAG) in Open WebUI - the function handles context retrieval automatically
2. **Configure the function settings** with your RAG endpoint URL and API key
3. **Enable the function globally** for it to work across all conversations
4. **Monitor function logs** with: `docker logs -f open-webui`

### RAG Function Notes

- Set explicit system prompts if you experience weird model output
- The function can be configured per-model if needed (instead of globally)
- For advanced conversation context management, consider enhancing the function with an LLM call to improve query enhancement
- The function gracefully handles cases where RAG context is not available

## Troubleshooting

- **Can't connect**: Ensure your URL includes `/v1` at the end
- **No models showing**: Check your API key and endpoint URL
- **RAG not working**: Verify RAG endpoint URL and API key in function settings
- **Weird model responses**: Set an explicit system prompt in Open WebUI

## Additional Resources

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Open WebUI GitHub](https://github.com/open-webui/open-webui)
- [ConfidentialMind Documentation](https://docs.confidentialmind.com)