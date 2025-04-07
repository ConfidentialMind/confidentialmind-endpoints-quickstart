# confidentialmind-endpoints-quickstart
Quickstart guides for interacting with different endpoints


## Structure (remove after done)

README.md (generic introduction and pointer to model and rag start)

- /model-endpoint
  - README.md (introduction to us having OpenAI api like interface and examples on how to run the test scripts with installing dependencies from requirements)
  - .env.example (example on how to set envs (URL and API key))
  - chat.py (example using http requests)
  - chat-openai-sdk.py (same example but using python SDK)
  - multimodal.py (send image file with question, have a sample image file in the repo)
  - /test-data/image.png (picture of table or other interesting multimodal use case)
  - requirements.txt (deps so that all scripts are runnable)
- /rag-endpoint
  - README.md (link to our RAG documentation, basic info of RAG, how to run the files)
  - .env.example (example on how to set envs (URL and API key))
  - send-files.py (send files to endpoint, send all files in /test-data folder)
  - get-files.py (get all files currently in the system)
  - chat.py (example /chat/completions using http requests)
  - /test-data/whitepaper.pdf (our whitepaper or other test material)
  - requirements.txt (deps so that all scripts are runnable)
- /agent-endpoint
  - README.md (link to agent repo)

### Some ideas for the future
- Add complete RAG command line tool. Or make PIP release out of the tool -> make it easily runnable
