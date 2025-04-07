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

## Usage Examples

### Uploading Documents

Upload documents from the test-data folder:

```bash
python send-files.py
```

Upload from a specific directory:

```bash
python send-files.py --dir ./my-documents
```

Upload a single file:

```bash
python send-files.py --file ./test-data/whitepaper.pdf
```

### Viewing Documents

List all uploaded documents:

```bash
python get-files.py
```

### Chatting with Your Documents

Start an interactive chat:

```bash
python chat.py
```

Ask a single question:

```bash
python chat.py --query "What can I do with the ConfidentialMind stack?"
```

### Cleaning Up

Delete files from a specific upload:

```bash
python delete-files.py --from-json uploaded_files_20240407_120000.json
```

Delete all uploaded files:

```bash
python delete-files.py --all
```

Skip confirmations:

```bash
python delete-files.py --all --yes
```

## More Information

For detailed documentation, visit our [official documentation](https://docs.confidentialmind.com/).