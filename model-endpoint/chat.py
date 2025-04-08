#!/usr/bin/env python
"""
Simple example of using our chat completion API with HTTP requests.
"""

import os
import requests
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
    
    # Prepare the API endpoint URL
    endpoint = f"{base_url}/chat/completions"
    
    # Set up headers with authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Example messages for the chat
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a quick fact about artificial intelligence."}
    ]
    
    # Create the request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    # Make the API request
    print(f"Sending request to {endpoint}...")
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse and print the response
        result = response.json()
        assistant_response = result["choices"][0]["message"]["content"]
        
        print("\nAPI Response:")
        print("-" * 40)
        print(assistant_response)
        print("-" * 40)
        
        # Print some additional information about the response
        print(f"\nInput tokens: {result.get('usage', {}).get('prompt_tokens', 'N/A')}")
        print(f"Completion tokens: {result.get('usage', {}).get('completion_tokens', 'N/A')}")
        print(f"Total tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()