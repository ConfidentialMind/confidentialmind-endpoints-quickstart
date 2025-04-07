#!/usr/bin/env python
"""
Example of using our chat completion API with streaming responses via the OpenAI SDK.
This demonstrates real-time text generation with a simple implementation.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API credentials from environment variables
    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL_NAME")
    
    # Verify credentials are available
    if not base_url or not api_key:
        print("Error: BASE_URL and API_KEY must be set in .env file")
        return
    
    # Ensure base_url ends with /v1
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    
    print(f"Initializing client with {base_url}...")
    
    # Initialize the OpenAI client with our API endpoint
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    
    # Example messages for the chat
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the concept of transfer learning in AI."}
    ]
    
    # Make the streaming API request
    print("Sending streaming request to chat completions API...")
    try:
        # Create a streaming completion
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            stream=True  # Enable streaming
        )
        
        print("\nStreaming response:")
        print("-" * 60)
        
        # Process the streaming response
        full_response = ""
        for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end='', flush=True)
                    full_response += content
        
        print("\n" + "-" * 60)
        print(f"\nFull response length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()