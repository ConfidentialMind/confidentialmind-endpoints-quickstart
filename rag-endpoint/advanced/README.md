# Advanced RAG API Examples

This directory contains more comprehensive examples showcasing the full capabilities of the RAG API.

## Why Advanced Examples?

While the main examples are designed to be simple and easy to understand, these advanced examples demonstrate:

- All available parameters for each endpoint
- More complex usage patterns
- Detailed error handling and logging
- Real-world integration scenarios

## Available Examples with Default Parameters

### Files and Document Management (`files_advanced.py`)

Upload files with all supported parameters:

**Default parameters:**
- **User ID:** `example-user`
- **Document ID:** auto-generated (optional parameter)
- **Group IDs:** `documentation` (single group for better retrieval compatibility)
- **Metadata:** `{"source": "example", "department": "Engineering", "category": "Documentation"}`
- **Directory:** Automatically finds test-data directory whether run from root or advanced folder

### Context Retrieval (`retrieval_advanced.py`)

Advanced context retrieval with filtering:

**Default parameters:**
- **Query:** "How do I upload files to the RAG endpoint?"
- **Max chunks:** 4
- **Group ID:** `documentation`
- **Filter IDs:** None (optional)
- **Metadata filters:** None (optional)

### Chat and Completion (`chat_advanced.py`)

Advanced chat features with filtering:

**Default parameters:**
- **Query:** "How do I upload files to the RAG endpoint?"
- **Max chunks:** 4
- **Group ID:** `documentation`
- **Temperature:** 0.7
- **Max tokens:** 500
- **Stream:** False
- **Filter IDs:** None (optional)
- **Metadata filters:** None (optional)

## Complete Filtering Workflow (Recommended Approach)

This workflow demonstrates how to effectively organize documents using both group IDs (primary) and metadata (secondary) filtering methods:

### Step 1: Upload Documents with Appropriate Organization

```bash
# 1. Upload product whitepaper with group ID and metadata
python files_advanced.py \
  --file ../test-data/ConfidentialMind-Whitepaper.pdf \
  --group-ids "product" \
  --metadata '{"type": "whitepaper", "department": "product-team"}'

# 2. Upload RAG API docs with group ID and metadata
python files_advanced.py \
  --file ../test-data/rag-endpoint.md \
  --group-ids "api-docs" \
  --metadata '{"type": "api-docs", "api-type": "rag", "department": "engineering"}'

# 3. Upload Model API docs with group ID and metadata (if available)
python files_advanced.py \
  --file ../test-data/model-endpoint.md \
  --group-ids "api-docs" \
  --metadata '{"type": "api-docs", "api-type": "model", "department": "engineering"}'
```

### Step 2: Demonstrate Group ID Filtering (Primary Method)

```bash
# Filter by group ID to get only product information
python retrieval_advanced.py \
  --group-id "product" \
  --query "What is ConfidentialMind?" \
  --verbose

# Filter by group ID to get all API documentation
python retrieval_advanced.py \
  --group-id "api-docs" \
  --query "How do API endpoints work?" \
  --verbose
```

### Step 3: Demonstrate Metadata Filtering (Secondary Method)

```bash
# Use metadata filtering to get only RAG API documentation
python retrieval_advanced.py \
  --metadata-filter "api-type:eq:rag" \
  --group-id "api-docs" \
  --query "How does the RAG API work?" \
  --verbose

# Use metadata filtering to get only content from the product team
python retrieval_advanced.py \
  --metadata-filter "department:eq:product-team" \
  --query "What does the product team say about ConfidentialMind?" \
  --group-id "product" \
  --verbose
```

### Step 4: Advanced Chat with Filtered Content

```bash
# Chat using group ID filtering to focus on API docs
python chat_advanced.py \
  --filter-group "api-docs" \
  --query "Explain the API endpoints"

# Chat with streaming using metadata filtering
python chat_advanced.py \
  --stream \
  --filter-metadata "department:eq:engineering" \
  --query "What engineering documentation is available?"
```

## Integration with the Basic Examples

Start with the simpler examples in the parent directory to learn the core concepts. Then explore these advanced examples when you need more control over your RAG API integration.

All of these advanced examples are set up with sensible defaults that work with the sample documents, so you can run them immediately to see how they work.