#!/usr/bin/env python
"""
Example of implementing a multi-turn chat interface using the OpenAI Python SDK.
This demonstrates how to maintain conversation history across multiple interactions.
"""
import os
import time
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
    
    # Initialize conversation history with a system message
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    print("\n" + "=" * 50)
    print("Welcome to the Chat Interface Example")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to reset the conversation history")
    print("=" * 50 + "\n")
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye!")
            break
        
        # Check for clear history command
        if user_input.lower() == "clear":
            messages = [{"role": "system", "content": "You are a helpful assistant."}]
            print("\nConversation history has been cleared.")
            continue
        
        # Add user message to conversation history
        messages.append({"role": "user", "content": user_input})
        
        # Make the API request
        try:
            # Show a simple "thinking" animation
            print("\nAssistant: ", end="", flush=True)
            for _ in range(3):
                time.sleep(0.3)
                print(".", end="", flush=True)
            print("\b" * 3, end="", flush=True)
            print(" " * 3, end="", flush=True)
            print("\b" * 3, end="", flush=True)
            
            # Send request to the API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            # Extract the response
            assistant_response = response.choices[0].message.content
            
            # Print the assistant's response
            print(f"\nAssistant: {assistant_response}")
            
            # Add assistant's response to conversation history
            messages.append({"role": "assistant", "content": assistant_response})
            
            # Print token usage for this interaction (optional)
            print(f"\n[Token usage for this interaction - Input: {response.usage.prompt_tokens}, "
                  f"Output: {response.usage.completion_tokens}, "
                  f"Total: {response.usage.total_tokens}]")
            
        except Exception as e:
            print(f"\nError: {e}")
            
        # Display conversation length (optional, helps developers see history growth)
        print(f"[Conversation history: {len(messages)} messages]")


if __name__ == "__main__":
    main()