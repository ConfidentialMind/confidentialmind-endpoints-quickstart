# RAG Endpoint

The RAG (Retrieval-Augmented Generation) Endpoint is a flexible and modular system built to enhance LLM responses with relevant context from your own documents. This system provides a standardized API for document ingestion, context retrieval, and augmented generation.

## Base URL and Authentication

All requests to the RAG endpoint must include:

1. **Base URL**: Your endpoint-specific base URL obtained from the portal
   ```bash
   https://api.example.com/v1/api/{endpoint-id}
   ```

2. **Authorization Header**: Your API key in the Authorization header
   ```bash
   Authorization: Bearer your-api-key-from-portal
   ```

## API Reference

### Files API

The `/files` endpoint provides a RESTful interface for managing files in the system.

#### Upload a File

```bash
POST {base_url}/files
```

**Headers:**
- `Authorization: Bearer your-api-key`
- `Content-Type: multipart/form-data`

**Parameters:**
- `file`: File data (required)
- `user_id`: ID of the user uploading the file (optional, defaults to "system")
- `document_id`: Custom ID for the document (optional, auto-generated if not provided)
- `group_ids`: List of group IDs to associate with the file (optional)
- `metadata`: JSON string of additional metadata (optional)

**Example metadata:**
```json
{
  "source": "email",
  "author": "John Doe",
  "tags": ["important", "reference"],
  "custom_field": "value"
}
```

**Response:**
```json
{
  "id": "document_id",
  "filename": "example.pdf",
  "created_at": 1677409068,
  "status": "processed"
}
```

#### List Files

```bash
GET {base_url}/files
```

**Headers:**
- `Authorization: Bearer your-api-key`

**Query Parameters:**
- `user_id`: Filter files by user ID (optional)
- `group_id`: Filter files by group ID (optional)

**Response:**
```json
{
  "files": [
    {
      "id": "doc_123",
      "user_id": "user_456",
      "group_ids": ["group_789", "group_101"],
      "metadata": {
        "filename": "report.pdf",
        "created_at": "2025-02-26T12:32:39.265082",
        "source": "upload",
        "author": "Jane Smith"
      }
    }
  ]
}
```

#### Delete a File

```bash
DELETE {base_url}/files/{file_id}
```

**Headers:**
- `Authorization: Bearer your-api-key`

**Parameters:**
- `file_id`: ID of the file to delete (path parameter)

**Response:**
```json
{
  "success": true,
  "message": "File doc_123 deleted successfully",
  "files_deleted": ["doc_123"]
}
```

### Context API

The `/context` endpoint provides a flexible way to retrieve relevant chunks of text from your document repository based on a query.

```bash
POST {base_url}/context
```

**Headers:**
- `Authorization: Bearer your-api-key`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "query": "your search query",
  "max_chunks": 4,
  "filter_ids": ["doc1", "doc2"],
  "group_id": "group1",
  "user_id": "user123",
  "metadata_filters": [
    {
      "field": "author",
      "value": "Alice",
      "operator": "eq"
    },
    {
      "field": "rating",
      "value": 4.5,
      "operator": "gt"
    }
  ]
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | The search query to find relevant text chunks |
| `max_chunks` | integer | No | 4 | Maximum number of chunks to return |
| `filter_ids` | array | No | null | List of document IDs to restrict the search to |
| `group_id` | string | No | null | Group ID to filter documents by (for permission-based filtering) |
| `user_id` | string | No | null | User ID to filter documents by (only returns documents owned by this user) |
| `metadata_filters` | array | No | null | List of metadata filters to apply |

**Metadata Filters:**

Each metadata filter object supports:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field` | string | Yes | Metadata field path (e.g., "author" or "details.category") |
| `value` | any | Yes | Value to match against the field |
| `operator` | string | No | Operator to use (default: "eq") |

Supported operators:
- `eq`: Equal to (default)
- `gt`: Greater than (for numeric values)
- `lt`: Less than (for numeric values)
- `contains`: Contains value (for strings) or contains element (for arrays)

**Response:**
```json
{
  "chunks": [
    "This is a document about Python programming...",
    "Machine learning frameworks in Python include..."
  ],
  "scores": [0.92, 0.87],
  "files": [
    {
      "id": "doc1",
      "user_id": "user123",
      "group_ids": ["group1", "group2"],
      "metadata": {
        "author": "Alice",
        "topic": "programming",
        "tags": ["python", "beginner"],
        "rating": 4.5
      },
      "top_score": 0.92,
      "n_chunks": 1
    },
    {
      "id": "doc2",
      "user_id": "user456",
      "group_ids": ["group1"],
      "metadata": {
        "author": "Bob",
        "topic": "machine learning",
        "tags": ["python", "advanced"],
        "rating": 4.8
      },
      "top_score": 0.87,
      "n_chunks": 1
    }
  ]
}
```

### Chat Completions API

Generate completions with context-aware responses using an OpenAI-compatible API.

```bash
POST {base_url}/v1/chat/completions
```

**Headers:**
- `Authorization: Bearer your-api-key`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "model": "cm-llm",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What are the key features of the product?"}
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "max_chunks": 3
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | The model to use (typically "cm-llm") |
| `messages` | array | Yes | - | Array of messages in the conversation |
| `temperature` | number | No | 0.7 | Controls randomness (0-1) |
| `max_tokens` | integer | No | 500 | Maximum number of tokens to generate |
| `max_chunks` | integer | No | 4 | Maximum number of context chunks to retrieve |
| `stream` | boolean | No | false | Whether to stream the response |

**Response (non-streaming):**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "cm-llm",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the documentation, the key features of the product include..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 320,
    "total_tokens": 345
  }
}
```

### Groups API

Manage document groups for organization and access control.

#### List Groups

```bash
GET {base_url}/groups
```

**Headers:**
- `Authorization: Bearer your-api-key`

**Response:**
```json
{
  "groups": ["group1", "group2", "group3"]
}
```

#### Get Group Information

```bash
GET {base_url}/groups/{group_id}
```

**Headers:**
- `Authorization: Bearer your-api-key`

**Response:**
```json
{
  "group_id": "group1",
  "document_count": 42,
  "created_at": "2023-05-15T12:00:00Z",
  "last_updated": "2023-10-28T14:30:22Z"
}
```

#### Get Group Documents

```bash
GET {base_url}/groups/{group_id}/documents
```

**Headers:**
- `Authorization: Bearer your-api-key`

**Response:**
```json
{
  "group_id": "group1",
  "document_count": 42,
  "documents": [
    {
      "id": "doc1",
      "user_id": "user123",
      "group_ids": ["group1", "group2"],
      "metadata": {
        "filename": "example.txt",
        "created_at": "2023-10-15T10:30:00Z",
        "tags": ["report", "finance"]
      }
    }
  ]
}
```

## Code Examples

### Upload Files

```python
from pathlib import Path
import requests

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}"
}

file_path = Path("/path/to/your/document.txt")

# Upload a single file
with open(file_path, 'rb') as file:
    response = requests.post(
        f"{api_base_url}/files",
        headers=headers,
        files={"file": (file_path.name, file, "application/octet-stream")}
    )

file_id = response.json()["id"]
print(f"File uploaded with ID: {file_id}")
```

### Get Context

```python
import requests

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "query": "What are the key features of the product?",
    "max_chunks": 3,
    "user_id": "user123"  # Filter to only documents owned by this user
}

response = requests.post(
    f"{api_base_url}/context", 
    headers=headers,
    json=payload
)
result = response.json()

for i, (chunk, score) in enumerate(zip(result["chunks"], result["scores"])):
    print(f"Chunk {i + 1} (score: {score:.2f}): {chunk[:100]}...")
```

### Generate Chat Completions

```python
import requests

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "cm-llm",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the key features of the product?"}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "max_chunks": 3
}

response = requests.post(
    f"{api_base_url}/v1/chat/completions", 
    headers=headers,
    json=payload
)
result = response.json()

print("Assistant response:", result["choices"][0]["message"]["content"])
```

### Streaming Example

```python
import requests
import json

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "cm-llm",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the key features of the product?"}
    ],
    "temperature": 0.7,
    "stream": True,
    "max_chunks": 3
}

response = requests.post(
    f"{api_base_url}/v1/chat/completions", 
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

### OpenAI SDK Integration

```python
from openai import OpenAI

# Configuration from portal
api_base_url = "https://api.example.com/v1/api/your-endpoint-id"
api_key = "your-api-key-from-portal"

# Initialize client with base URL and API key
client = OpenAI(
    base_url=f"{api_base_url}/v1/",  # Note the addition of "/v1/"
    api_key=api_key
)

# Make a request
response = client.chat.completions.create(
    model="cm-llm",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the key features of the product?"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
```

## When to use `/context` vs `/v1/chat/completions`

- Use `/context` when you:
  - Need to retrieve relevant passages without generating LLM responses
  - Want to implement custom processing on the retrieved context
  - Are building a search interface that shows document snippets
  - Need to debug or evaluate the retrieval component separately

- Use `/v1/chat/completions` when you:
  - Need complete LLM responses that incorporate the retrieved context
  - Want a drop-in replacement for OpenAI's chat API with RAG capabilities
  - Need to maintain conversational context with retrieved information

## Best Practices

- For optimal results, use clear and specific questions that match how information is presented in your documentation
- Use the `max_chunks` parameter to control how much context is retrieved (3-5 is usually optimal)
- Apply metadata filters to narrow down results when you have a large document repository
- For categorized documents, use the `group_id` parameter to search within specific document groups
- Use the `user_id` parameter when you need to restrict context retrieval to documents owned by a specific user
- Consider using lower temperature (0.0-0.3) for more factual responses based on your documentation