# RAG Endpoint Quickstart

This directory contains simple examples for getting started with our Retrieval-Augmented Generation (RAG) API.

## What is RAG?

Retrieval-Augmented Generation (RAG) enhances AI responses by retrieving relevant information from your documents before generating answers. Upload your documents, ask questions, and get contextually informed responses.

## Setup

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Edit the `.env` file to set your API URL and key.

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Example Workflow

Follow these steps to try out the complete RAG workflow with our example scripts:

### 1. Upload Your Documents

Upload the included sample documents:

```bash
python send-files.py
```

This will upload the example documents in the `test-data` directory:
- `ConfidentialMind-Whitepaper.pdf`: Product whitepaper
- `rag-endpoint.md`: API documentation

### 2. View Your Uploaded Documents

List all your uploaded documents:

```bash
python get-files.py
```

This shows all documents you've uploaded, including their IDs and metadata.

### 3. Retrieve Context from Your Documents

Get relevant information chunks about document uploads:

```bash
python context.py
```

The default query is "How do I upload files to the RAG endpoint?" but you can specify your own:

```bash
python context.py --query "What are the key features of the ConfidentialMind product?"
```

### 4. Chat with Your Documents

Start an interactive chat with your documents:

```bash
python chat.py
```

Or ask a single question:

```bash
python chat.py --query "How can I upload files to the RAG system?"
```

### 5. Clean Up (When Finished)

When you're done experimenting, you can delete your uploaded files:

```bash
python delete-files.py --all
```

## Advanced Examples with Document Filtering

For more sophisticated usage patterns with filtering capabilities, explore the [advanced](./advanced) directory:

```bash
# Upload the whitepaper with specific metadata for filtering demo
python advanced/files_advanced.py --file ./test-data/ConfidentialMind-Whitepaper.pdf \
                                 --metadata '{"source": "whitepaper", "department": "Engineering"}'

# Upload markdown doc with different metadata
python advanced/files_advanced.py --file ./test-data/rag-endpoint.md \
                                 --metadata '{"source": "documentation", "department": "Product"}'

# Demonstrate metadata filtering - get only whitepaper content
python advanced/retrieval_advanced.py --metadata-filter "source:eq:whitepaper" --verbose

# Chat using only content from the Product department
python advanced/chat_advanced.py --filter-metadata "department:eq:Product"
```

Each advanced script provides detailed help with `--help` explaining all available options.

## More Information

For detailed documentation, visit our [official documentation](https://docs.confidentialmind.com).