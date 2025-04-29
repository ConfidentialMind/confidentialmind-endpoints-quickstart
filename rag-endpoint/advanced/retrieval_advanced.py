#!/usr/bin/env python3
"""
Advanced example of retrieving context from the RAG API with all filtering options.

This example demonstrates:
- Basic context retrieval with a query
- Filtering by document IDs
- Filtering by group ID
- Advanced metadata filtering with various operators
- Combining multiple filters for precise retrieval
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Union, Any

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table


def get_context_advanced(
    base_url: str,
    query: str,
    max_chunks: int = 8,
    filter_ids: Optional[List[str]] = None,
    group_id: Optional[str] = None,
    metadata_filters: Optional[List[Dict[str, Any]]] = None,
    api_key: Optional[str] = None
):
    """
    Retrieve context from the RAG system with advanced filtering options.
    
    Args:
        base_url: Base URL of the RAG API
        query: Search query to find relevant text chunks
        max_chunks: Maximum number of chunks to return
        filter_ids: Optional list of document IDs to restrict the search to
        group_id: Optional group ID to filter documents by
        metadata_filters: Optional list of metadata filters to apply
        api_key: API key for authentication
        
    Returns:
        Response JSON from the API
    """
    url = f"{base_url}/context"
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Build request payload
    payload = {
        "query": query,
        "max_chunks": max_chunks
    }
    
    # Add optional filtering parameters if provided
    if filter_ids:
        payload["filter_ids"] = filter_ids
    if group_id:
        payload["group_id"] = group_id
    if metadata_filters:
        payload["metadata_filters"] = metadata_filters
    
    # Make the request
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


def main():
    """Main function to parse arguments and retrieve context with advanced options."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API URL and key from environment
    rag_api_url = os.getenv("RAG_API_URL")
    rag_api_key = os.getenv("RAG_API_KEY")
    
    # Ensure we have the required environment variables
    if not rag_api_url:
        print("Error: RAG_API_URL not set in environment or .env file")
        return 1
    
    parser = argparse.ArgumentParser(
        description='Advanced example: Retrieve context from the RAG API with filtering options'
    )
    
    # Basic parameters
    parser.add_argument('--query', '-q',
                        default="How do I upload files to the RAG endpoint?",
                        help='Search query to find relevant text chunks (default: "How do I upload files to the RAG endpoint?")')
    parser.add_argument('--max-chunks', '-c', type=int, default=4,
                        help='Maximum number of chunks to return (default: 4)')
    
    # Advanced filtering parameters
    filter_group = parser.add_argument_group('Advanced Filtering Options')
    filter_group.add_argument('--filter-ids', '-f', nargs='+',
                        help='List of document IDs to restrict the search to (e.g., doc_123 doc_456)')
    filter_group.add_argument('--group-id', '-g', default="documentation",
                        help='Group ID to filter documents by (default: "documentation")')
    filter_group.add_argument('--metadata-filter', '-m', action='append',
                        help='Metadata filter in format field:operator:value (e.g., "department:eq:Engineering")')
    
    # Output options
    parser.add_argument('--output-json', '-o',
                        help='Write raw JSON response to the specified file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose output including request payload')
    
    args = parser.parse_args()
    
    console = Console()
    
    # Parse filter IDs if comma-separated string is provided
    filter_ids = args.filter_ids
    if filter_ids and len(filter_ids) == 1 and ',' in filter_ids[0]:
        filter_ids = [id.strip() for id in filter_ids[0].split(',') if id.strip()]
    
    # Parse metadata filters if provided
    metadata_filters = None
    if args.metadata_filter:
        metadata_filters = [parse_metadata_filter(f) for f in args.metadata_filter]
    
    # Show the request being made if in verbose mode
    if args.verbose:
        console.print("[bold]Query:[/bold]", args.query)
        console.print("[bold]Max chunks:[/bold]", args.max_chunks)
        
        if filter_ids:
            console.print("[bold]Filtering by document IDs:[/bold]", ", ".join(filter_ids))
        if args.group_id:
            console.print("[bold]Filtering by group ID:[/bold]", args.group_id)
        if metadata_filters:
            console.print("[bold]Metadata filters:[/bold]")
            for filter_obj in metadata_filters:
                console.print(f"  - {filter_obj['field']} {filter_obj['operator']} {filter_obj['value']}")
        
        # Show the complete API payload
        payload = {
            "query": args.query,
            "max_chunks": args.max_chunks
        }
        if filter_ids:
            payload["filter_ids"] = filter_ids
        if args.group_id:
            payload["group_id"] = args.group_id
        if metadata_filters:
            payload["metadata_filters"] = metadata_filters
        
        console.print("\n[bold]Complete API payload:[/bold]")
        console.print_json(json.dumps(payload))    
    try:
        # Get context with advanced filtering
        result = get_context_advanced(
            base_url=rag_api_url,
            query=args.query,
            max_chunks=args.max_chunks,
            filter_ids=filter_ids,
            group_id=args.group_id,
            metadata_filters=metadata_filters,
            api_key=rag_api_key
        )
        
        # Save raw JSON if requested
        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(result, f, indent=2)
                console.print(f"[green]Raw JSON response saved to {args.output_json}[/green]")
        
        # Display the results
        display_context_results(result)
    
    except ValueError as e:
        # Handle validation errors
        console.print(f"[bold red]Validation error: {str(e)}[/bold red]")
        return 1
    except Exception as e:
        # Handle other errors
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