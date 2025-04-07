#!/usr/bin/env python3
"""
Simple example of using our RAG-enabled chat completion API.
"""

import argparse
import os
import sys
from typing import List, Dict

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown


def chat_completion(base_url: str, api_key: str, model: str, messages: List[Dict], 
                    max_chunks: int = 4, temperature: float = 0.5):
    """Send a chat completion request to the RAG API."""
    url = f"{base_url}/v1/chat/completions"
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_chunks": max_chunks
    }
    
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    
    return response.json()


def interactive_chat(base_url: str, api_key: str, model: str, max_chunks: int = 4, temperature: float = 0.5):
    """Start an interactive chat session with the RAG API."""
    console = Console()
    console.print("[bold]RAG Chat Session[/bold]")
    console.print("[dim]Type 'exit', 'quit', or press Ctrl+C to end the session.[/dim]")
    console.print()
    
    # Initialize message history
    messages = []
    
    try:
        while True:
            # Get user input
            user_message = console.input("[bold blue]You:[/bold blue] ")
            
            # Check for exit commands
            if user_message.lower() in ("exit", "quit"):
                break
            
            # Add user message to history
            messages.append({"role": "user", "content": user_message})
            
            try:
                # Get completion
                result = chat_completion(
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    messages=messages,
                    max_chunks=max_chunks,
                    temperature=temperature
                )
                
                # Display the assistant's response
                if "choices" in result and result["choices"]:
                    message = result["choices"][0]["message"]
                    content = message["content"]
                    
                    console.print("\n[bold green]Assistant:[/bold green]")
                    try:
                        # Try to render as markdown
                        md = Markdown(content)
                        console.print(md)
                    except Exception:
                        # Fall back to plain text
                        console.print(content)
                    
                    # Add assistant response to history
                    messages.append(message)
                    
                    # Show token usage if available
                    if "usage" in result:
                        usage = result["usage"]
                        console.print("\n[dim]Token Usage:[/dim]")
                        console.print(f"[dim]- Prompt tokens: {usage.get('prompt_tokens', 'N/A')}[/dim]")
                        console.print(f"[dim]- Completion tokens: {usage.get('completion_tokens', 'N/A')}[/dim]")
                        console.print(f"[dim]- Total tokens: {usage.get('total_tokens', 'N/A')}[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    except KeyboardInterrupt:
        console.print("\n[dim]Chat session ended.[/dim]")


def main():
    """Main function to parse arguments and handle chat."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API URL and key from environment
    rag_api_url = os.getenv("RAG_API_URL")
    rag_api_key = os.getenv("RAG_API_KEY")
    rag_model = os.getenv("RAG_MODEL", "cm-llm")
    
    # Ensure we have the required environment variables
    if not rag_api_url:
        print("Error: RAG_API_URL not set in environment or .env file")
        return 1
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Chat with the RAG API')
    parser.add_argument('--query', '-q', help='Single query mode (non-interactive)')
    parser.add_argument('--max-chunks', '-c', type=int, default=4,
                        help='Maximum number of context chunks to retrieve (default: 4)')
    parser.add_argument('--temperature', '-t', type=float, default=0.5,
                        help='Temperature for text generation (default: 1.0)')
    
    args = parser.parse_args()
    
    try:
        if args.query:
            # Single query mode
            messages = [{"role": "user", "content": args.query}]
            
            # Get completion
            result = chat_completion(
                base_url=rag_api_url,
                api_key=rag_api_key,
                model=rag_model,
                messages=messages,
                max_chunks=args.max_chunks,
                temperature=args.temperature
            )
            
            # Display the result
            console = Console()
            if "choices" in result and result["choices"]:
                message = result["choices"][0]["message"]
                content = message["content"]
                
                console.print("\n[bold green]Assistant:[/bold green]")
                try:
                    # Try to render as markdown
                    md = Markdown(content)
                    console.print(md)
                except Exception:
                    # Fall back to plain text
                    console.print(content)
                
                # Show token usage if available
                if "usage" in result:
                    usage = result["usage"]
                    console.print("\n[dim]Token Usage:[/dim]")
                    console.print(f"[dim]- Prompt tokens: {usage.get('prompt_tokens', 'N/A')}[/dim]")
                    console.print(f"[dim]- Completion tokens: {usage.get('completion_tokens', 'N/A')}[/dim]")
                    console.print(f"[dim]- Total tokens: {usage.get('total_tokens', 'N/A')}[/dim]")
        
        else:
            # Interactive chat mode
            interactive_chat(
                base_url=rag_api_url,
                api_key=rag_api_key,
                model=rag_model,
                max_chunks=args.max_chunks,
                temperature=args.temperature
            )
    
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())