#!/usr/bin/env python
"""
Simple example of using our chat completion API with the OpenAI Python SDK.
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
        {"role": "user", "content": "Write a short haiku about technology."}
    ]
    
    # Make the API request
    print("Sending request to chat completions API...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract and print the response
        assistant_response = response.choices[0].message.content
        
        print("\nAPI Response:")
        print("-" * 40)
        print(assistant_response)
        print("-" * 40)
        
        # Print some additional information about the response
        print(f"\nInput tokens: {response.usage.prompt_tokens}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()