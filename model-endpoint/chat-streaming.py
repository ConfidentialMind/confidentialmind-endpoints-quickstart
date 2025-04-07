#!/usr/bin/env python
"""
Example of using our chat completion API with streaming responses via HTTP requests.
This demonstrates how to process server-sent events for real-time text generation.
"""

import os
import json
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
        {"role": "user", "content": "Write a paragraph explaining how machine learning works."}
    ]
    
    # Create the request payload with streaming enabled
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300,
        "stream": True  # Enable streaming
    }
    
    print(f"Sending streaming request to {endpoint}...")
    
    try:
        # Make a streaming request
        response = requests.post(endpoint, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        
        print("\nStreaming response:")
        print("-" * 60)
        
        # Process the streaming response
        collected_chunks = []
        
        # Iterate through the stream of server-sent events
        for line in response.iter_lines():
            if line:
                # Decode the line
                line = line.decode('utf-8')
                
                # Skip lines that don't start with "data:"
                if not line.startswith('data:'):
                    continue
                
                # Remove the "data:" prefix
                line = line[5:].strip()
                
                # Check for the end of the stream
                if line == "[DONE]":
                    break
                
                # Parse the JSON data
                try:
                    json_data = json.loads(line)
                    chunk = json_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                    collected_chunks.append(json_data)
                    print(chunk, end='', flush=True)  # Print the chunk without a newline
                except json.JSONDecodeError:
                    print(f"Error parsing JSON from: {line}")
        
        print("\n" + "-" * 60)
        
        # Calculate token usage from the collected chunks (if available)
        if collected_chunks and 'usage' in collected_chunks[-1]:
            usage = collected_chunks[-1]['usage']
            print(f"\nCompletion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"Total tokens: {usage.get('total_tokens', 'N/A')}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()