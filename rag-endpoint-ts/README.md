# RAG Endpoint Quickstart (TypeScript)

This directory contains TypeScript examples for getting started with our Retrieval-Augmented Generation (RAG) API.

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
npm install
```

## Usage Examples

### Uploading Documents

Upload documents from the test-data folder:

```bash
npm run send-files
```

Upload from a specific directory:

```bash
npm run send-files -- --dir ./my-documents
```

Upload a single file:

```bash
npm run send-files -- --file ./test-data/ConfidentialMind-Whitepaper.pdf
```

### Viewing Documents

List all uploaded documents:

```bash
npm run get-files
```

### Chatting with Your Documents

Start an interactive chat:

```bash
npm run chat
```

Ask a single question:

```bash
npm run chat -- --query "What can I do with the ConfidentialMind stack?"
```

### Cleaning Up

Delete files from a specific upload:

```bash
npm run delete-files -- --from-json uploaded_files_20240407_120000.json
```

Delete all uploaded files:

```bash
npm run delete-files -- --all
```

Skip confirmations:

```bash
npm run delete-files -- --all --yes
```

## More Information

For detailed documentation, visit our [official documentation](https://docs.confidentialmind.com).