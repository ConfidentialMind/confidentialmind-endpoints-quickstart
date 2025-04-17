# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Setup
- Python: `pip install -r requirements.txt` in each directory
- TypeScript: `npm install` in each *-ts directory
- Run Python examples: `python <script>.py` (e.g., `python chat.py`)
- Run TypeScript examples: `npm run <script>` (e.g., `npm run chat`)
- Configure API credentials: Create `.env` file with BASE_URL, API_KEY, MODEL_NAME

## Python Code Style Guidelines
- Follow PEP 8 conventions
- Use 4 spaces for indentation
- Import order: built-in libraries, third-party libraries, local modules
- Module-level docstrings with triple double quotes (""")
- Function-level comments with # for implementation details
- Error handling: Use try/except with specific exceptions
- Clear variable naming (descriptive, lowercase with underscores)

## TypeScript Code Style Guidelines
- Use 2 spaces for indentation
- Import order: built-in modules, third-party modules, local modules
- Module-level comments with JSDoc (/** */)
- Interface definitions for request/response types
- Async/await for asynchronous operations
- Proper error handling with try/catch blocks
- Strong typing with interfaces and type annotations

## Best Practices
- Environment variables for credentials/configuration
- Request validation before API calls
- Comprehensive error handling for API requests
- Clean code structure with proper error handling
- TypeScript: Use interfaces for API request/response types