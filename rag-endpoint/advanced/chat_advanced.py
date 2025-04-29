#!/usr/bin/env python3
"""
Advanced example of using our RAG-enabled chat completion API with filtering options.

This example demonstrates:
- Basic chat completions
- Filtering results by document IDs
- Filtering by group ID
- Metadata-based filtering
- Streaming responses
- Setting advanced parameters like temperature and max_tokens
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Any

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel


def chat_completion_advanced(
    base_url: str, 
    api_key: str, 
    model: str, 
    messages: List[Dict],
    max_chunks: int = 8,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    filter_ids: Optional[List[str]] = None,
    group_id: Optional[str] = None,
    metadata_filters: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False
):
    """
    Send a chat completion request to the RAG API with advanced options.
    
    Args:
        base_url: Base URL of the RAG API
        api_key: API key for authentication
        model: Model to use for generating completions
        messages: List of message objects in the conversation
        max_chunks: Maximum number of context chunks to retrieve
        temperature: Controls randomness (0-1)
        max_tokens: Maximum number of tokens to generate
        filter_ids: Optional list of document IDs to restrict context to
        group_id: Optional group ID to filter documents by
        metadata_filters: Optional list of metadata filters to apply
        stream: Whether to stream the response
        
    Returns:
        Response JSON from the API or a generator if streaming
    """
    url = f"{base_url}/v1/chat/completions"
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Build request payload with all parameters
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_chunks": max_chunks,
        "stream": stream
    }
    
    # Add optional parameters if provided
    if max_tokens is not None:
        data["max_tokens"] = max_tokens
    if filter_ids:
        data["filter_ids"] = filter_ids
    if group_id:
        data["group_id"] = group_id
    if metadata_filters:
        data["metadata_filters"] = metadata_filters
    
    # Handle streaming vs non-streaming responses
    if stream:
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()
        
        def generate():
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        chunk_data = line[6:]  # Remove 'data: ' prefix
                        if chunk_data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(chunk_data)
                            yield chunk
                        except json.JSONDecodeError:
                            pass
        
        return generate()
    else:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()


def parse_metadata_filter(filter_str: str) -> Dict[str, Any]:
    """
    Parse a metadata filter string into a filter object.
    
    Format: field:operator:value
    Examples:
      - author:eq:John
      - rating:gt:4.5
      - tags:contains:python
    """
    parts = filter_str.split(':', 2)
    
    if len(parts) != 3:
        raise ValueError(f"Invalid metadata filter format: {filter_str}. Expected format: field:operator:value")
    
    field, operator, value = parts
    
    # Validate operator
    valid_operators = ['eq', 'gt', 'lt', 'contains']
    if operator not in valid_operators:
        raise ValueError(f"Invalid operator: {operator}. Must be one of: {', '.join(valid_operators)}")
    
    # Convert value to the appropriate type (number, boolean, or string)
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    else:
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            # Keep as string
            pass
    
    return {
        "field": field,
        "operator": operator,
        "value": value
    }


def interactive_chat_advanced(
    base_url: str, 
    api_key: str, 
    model: str,
    max_chunks: int = 8,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    filter_ids: Optional[List[str]] = None,
    group_id: Optional[str] = None,
    metadata_filters: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False
):
    """
    Start an interactive chat session with the RAG API using advanced options.
    
    Args:
        base_url: Base URL of the RAG API
        api_key: API key for authentication
        model: Model to use for generating completions
        max_chunks: Maximum number of context chunks to retrieve
        temperature: Controls randomness (0-1)
        max_tokens: Maximum number of tokens to generate
        filter_ids: Optional list of document IDs to restrict context to
        group_id: Optional group ID to filter documents by
        metadata_filters: Optional list of metadata filters to apply
        stream: Whether to stream the response
    """
    console = Console()
    console.print("[bold]Advanced RAG Chat Session[/bold]")
    console.print("[dim]Type 'exit', 'quit', or press Ctrl+C to end the session.[/dim]")
    
    # Show the active filters
    if filter_ids or group_id or metadata_filters:
        console.print("\n[bold cyan]Active Filters:[/bold cyan]")
        if filter_ids:
            console.print(f"[dim]- Document IDs: {', '.join(filter_ids)}[/dim]")
        if group_id:
            console.print(f"[dim]- Group ID: {group_id}[/dim]")
        if metadata_filters:
            console.print("[dim]- Metadata filters:[/dim]")
            for filter_obj in metadata_filters:
                console.print(f"[dim]  · {filter_obj['field']} {filter_obj['operator']} {filter_obj['value']}[/dim]")
    
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
                if stream:
                    # Handle streaming response
                    console.print("\n[bold green]Assistant:[/bold green]")
                    
                    # Set up variables to collect the streaming content
                    collected_content = ""
                    
                    # Use Live to update the display as content streams in
                    with Live("", refresh_per_second=10, console=console) as live:
                        stream_generator = chat_completion_advanced(
                            base_url=base_url,
                            api_key=api_key,
                            model=model,
                            messages=messages,
                            max_chunks=max_chunks,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            filter_ids=filter_ids,
                            group_id=group_id,
                            metadata_filters=metadata_filters,
                            stream=True
                        )
                        
                        for chunk in stream_generator:
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                collected_content += content
                                
                                # Update the live display with the current content
                                try:
                                    # Try to render as Markdown
                                    live.update(Markdown(collected_content))
                                except Exception:
                                    # Fall back to plain text
                                    live.update(collected_content)
                    
                    # Add assistant response to history
                    messages.append({"role": "assistant", "content": collected_content})
                    
                else:
                    # Get non-streaming completion
                    result = chat_completion_advanced(
                        base_url=base_url,
                        api_key=api_key,
                        model=model,
                        messages=messages,
                        max_chunks=max_chunks,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        filter_ids=filter_ids,
                        group_id=group_id,
                        metadata_filters=metadata_filters,
                        stream=False
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
                if hasattr(e, 'response') and e.response:
                    try:
                        error_json = e.response.json()
                        console.print("[red]API Error:[/red]")
                        console.print_json(json.dumps(error_json))
                    except:
                        console.print(f"[red]Response: {e.response.text}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[dim]Chat session ended.[/dim]")


def main():
    """Main function to parse arguments and handle advanced chat options."""
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
    parser = argparse.ArgumentParser(
        description='Advanced example: Chat with the RAG API using filtering options'
    )
    
    # Basic parameters
    parser.add_argument('--query', '-q', default="How do I upload files to the RAG endpoint?",
                        help='Single query mode (non-interactive) (default: "How do I upload files to the RAG endpoint?")')
    parser.add_argument('--max-chunks', '-c', type=int, default=4,
                        help='Maximum number of context chunks to retrieve (default: 4)')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                        help='Temperature for text generation (default: 0.7)')
    parser.add_argument('--max-tokens', type=int, default=500,
                        help='Maximum number of tokens to generate (default: 500)')
    parser.add_argument('--stream', '-s', action='store_true',
                        help='Stream the response in real-time')
    
    # Advanced filtering parameters
    filter_group = parser.add_argument_group('Advanced Filtering Options')
    filter_group.add_argument('--filter-ids', '-f', nargs='+',
                              help='List of document IDs to restrict context to (e.g., doc_123 doc_456)')
    filter_group.add_argument('--filter-group', '-g', default="documentation",
                              help='Group ID to filter documents by (default: "documentation")')
    filter_group.add_argument('--filter-metadata', '-m', action='append',
                              help='Metadata filter in format field:operator:value (e.g., "department:eq:Engineering")')
    
    args = parser.parse_args()
    
    console = Console()
    
    # Parse filter IDs if comma-separated string is provided
    filter_ids = args.filter_ids
    if filter_ids and len(filter_ids) == 1 and ',' in filter_ids[0]:
        filter_ids = [id.strip() for id in filter_ids[0].split(',') if id.strip()]
    
    # Parse metadata filters if provided
    metadata_filters = None
    if args.filter_metadata:
        try:
            metadata_filters = [parse_metadata_filter(f) for f in args.filter_metadata]
        except ValueError as e:
            console.print(f"[bold red]Error parsing metadata filter: {str(e)}[/bold red]")
            return 1
    
    try:
        if args.query:
            # Single query mode
            messages = [{"role": "user", "content": args.query}]
            
            # Show active filters and parameters
            if args.stream or args.filter_ids or args.filter_group or args.filter_metadata:
                console.print(f"\n[bold cyan]Query with advanced parameters:[/bold cyan]")
                console.print(f"[dim]- Query: \"{args.query}\"[/dim]")
                console.print(f"[dim]- Max chunks: {args.max_chunks}[/dim]")
                console.print(f"[dim]- Temperature: {args.temperature}[/dim]")
                console.print(f"[dim]- Max tokens: {args.max_tokens or 'default'}[/dim]")
                console.print(f"[dim]- Streaming: {args.stream}[/dim]")
                
                if args.filter_ids:
                    console.print(f"[dim]- Document filter: {', '.join(filter_ids)}[/dim]")
                if args.filter_group:
                    console.print(f"[dim]- Group filter: {args.filter_group}[/dim]")
                if metadata_filters:
                    console.print("[dim]- Metadata filters:[/dim]")
                    for filter_obj in metadata_filters:
                        console.print(f"[dim]  · {filter_obj['field']} {filter_obj['operator']} {filter_obj['value']}[/dim]")
                console.print()
            
            # Get completion with advanced options
            if args.stream:
                # Handle streaming response
                console.print("\n[bold green]Assistant:[/bold green]")
                
                # Set up variables to collect the streaming content
                collected_content = ""
                
                # Use Live to update the display as content streams in
                with Live("", refresh_per_second=10, console=console) as live:
                    stream_generator = chat_completion_advanced(
                        base_url=rag_api_url,
                        api_key=rag_api_key,
                        model=rag_model,
                        messages=messages,
                        max_chunks=args.max_chunks,
                        temperature=args.temperature,
                        max_tokens=args.max_tokens,
                        filter_ids=filter_ids,
                        group_id=args.filter_group,
                        metadata_filters=metadata_filters,
                        stream=True
                    )
                    
                    for chunk in stream_generator:
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            collected_content += content
                            
                            # Update the live display with the current content
                            try:
                                # Try to render as Markdown
                                live.update(Markdown(collected_content))
                            except Exception:
                                # Fall back to plain text
                                live.update(collected_content)
            else:
                # Non-streaming response
                result = chat_completion_advanced(
                    base_url=rag_api_url,
                    api_key=rag_api_key,
                    model=rag_model,
                    messages=messages,
                    max_chunks=args.max_chunks,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    filter_ids=filter_ids,
                    group_id=args.filter_group,
                    metadata_filters=metadata_filters,
                    stream=False
                )
                
                # Display the result
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
            # Interactive chat mode with advanced options
            interactive_chat_advanced(
                base_url=rag_api_url,
                api_key=rag_api_key,
                model=rag_model,
                max_chunks=args.max_chunks,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                filter_ids=filter_ids,
                group_id=args.filter_group,
                metadata_filters=metadata_filters,
                stream=args.stream
            )
    
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            try:
                error_json = e.response.json()
                console.print("[red]API Error:[/red]")
                console.print_json(json.dumps(error_json))
            except:
                console.print(f"[red]Response: {e.response.text}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())