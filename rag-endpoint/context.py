#!/usr/bin/env python3
"""
Simple example of retrieving context from the RAG API.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table


def get_context(
    base_url: str,
    query: str,
    max_chunks: int = 8,
    api_key: Optional[str] = None
):
    """Retrieve context from the RAG system."""
    url = f"{base_url}/context"
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Build request payload
    payload = {
        "query": query,
        "max_chunks": max_chunks
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()


def display_context_results(result: Dict):
    """Display context retrieval results in a formatted way."""
    console = Console()
    
    # Check if we got valid results
    if not result or "chunks" not in result or not result["chunks"]:
        console.print("[yellow]No context chunks found for your query.[/yellow]")
        return
    
    chunks = result.get("chunks", [])
    scores = result.get("scores", [0] * len(chunks))
    files = result.get("files", [])
    
    # Display the chunks with their scores
    console.print("\n[bold]Retrieved Context Chunks:[/bold]")
    
    for i, (chunk, score) in enumerate(zip(chunks, scores)):
        console.print(f"\n[bold cyan]Chunk {i+1}[/bold cyan] [dim](score: {score:.2f})[/dim]")
        # Use markdown rendering for the chunk text
        try:
            md = Markdown(chunk)
            console.print(md)
        except Exception:
            # Fallback to plain text
            console.print(chunk)
    
    # Display information about the source files
    if files:
        console.print("\n[bold]Source Files:[/bold]")
        
        table = Table()
        table.add_column("ID")
        table.add_column("User ID")
        table.add_column("Groups")
        table.add_column("Top Score")
        table.add_column("Chunks")
        table.add_column("Metadata")
        
        for file in files:
            file_id = file.get("id", "N/A")
            user_id = file.get("user_id", "N/A")
            groups = ", ".join(file.get("group_ids", []))
            top_score = f"{file.get('top_score', 0):.2f}"
            n_chunks = str(file.get("n_chunks", 0))
            
            # Format metadata for display
            metadata = file.get("metadata", {})
            if metadata:
                metadata_str = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
            else:
                metadata_str = "N/A"
            
            table.add_row(file_id, user_id, groups, top_score, n_chunks, metadata_str)
        
        console.print(table)


def parse_metadata_filter(filter_str: str) -> Dict:
    """Parse a metadata filter string into a filter object.
    
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


def main():
    """Main function to parse arguments and retrieve context."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API URL and key from environment
    rag_api_url = os.getenv("RAG_API_URL")
    rag_api_key = os.getenv("RAG_API_KEY")
    
    # Ensure we have the required environment variables
    if not rag_api_url:
        print("Error: RAG_API_URL not set in environment or .env file")
        return 1
    
    parser = argparse.ArgumentParser(description='Retrieve context from the RAG API')
    parser.add_argument('--query', '-q',
                        default="How do I upload files to the RAG endpoint?",
                        help='Search query to find relevant text chunks (default: "How do I upload files to the RAG endpoint?")')
    parser.add_argument('--max-chunks', '-c', type=int, default=3,
                        help='Maximum number of chunks to return (default: 3)')
    parser.add_argument('--output-json', '-o',
                        help='Write raw JSON response to the specified file')
    
    args = parser.parse_args()
    
    # Parse metadata filters if provided
    try:
        # Get context
        result = get_context(
            base_url=rag_api_url,
            query=args.query,
            max_chunks=args.max_chunks,
            api_key=rag_api_key
        )
        
        # Save raw JSON if requested
        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(result, f, indent=2)
                print(f"Raw JSON response saved to {args.output_json}")
        
        # Display the results
        display_context_results(result)
    
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())