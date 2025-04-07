#!/usr/bin/env python3
"""
Simple example of retrieving a list of files from the RAG API.
"""

import argparse
import os
import sys

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table


def get_files(base_url: str, api_key=None):
    """Retrieve a list of all files from the RAG system."""
    url = f"{base_url}/files"
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    
    # The API returns an object with a 'files' key containing the array of files
    if isinstance(result, dict) and 'files' in result:
        return result['files']
    
    # Fallback for different API response formats
    return result


def display_files(files):
    """Display file information in a table."""
    console = Console()
    
    if not files:
        console.print("[yellow]No files found in the system.[/yellow]")
        return

    # Check if files is a valid list of dictionaries
    if not isinstance(files, list) or (files and not isinstance(files[0], dict)):
        console.print("[red]Error: Unexpected response format from the API[/red]")
        console.print(f"[dim]Response: {files}[/dim]")
        return
    
    table = Table(title="Files in RAG System")
    
    # Add columns based on the first file's keys
    if files:
        columns = files[0].keys()
        for col in columns:
            table.add_column(col)
        
        # Add rows for each file
        for file in files:
            row = [str(file.get(col, "")) for col in columns]
            table.add_row(*row)
    
    console.print(table)


def main():
    """Main function to parse arguments and retrieve files."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API URL and key from environment
    rag_api_url = os.getenv("RAG_API_URL")
    rag_api_key = os.getenv("RAG_API_KEY")
    
    # Ensure we have the required environment variables
    if not rag_api_url:
        print("Error: RAG_API_URL not set in environment or .env file")
        return 1
    
    parser = argparse.ArgumentParser(description='List files in the RAG API')
    args = parser.parse_args()
    
    try:
        # Get and display files
        files = get_files(rag_api_url, rag_api_key)
        display_files(files)
    
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())