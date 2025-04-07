#!/usr/bin/env python3
"""
Simple example of uploading files to the RAG API.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table


def find_documents(directory_path: str):
    """Find all supported document files in a directory."""
    document_paths = []
    allowed_extensions = {'.pdf', '.docx', '.md', '.txt'}
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Walk through files in directory (non-recursive)
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            document_paths.append(str(file_path.absolute()))
    
    return document_paths


def upload_file(base_url: str, file_path: str, api_key=None):
    """Upload a single file to the RAG system."""
    url = f"{base_url}/files"
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'rb') as f:
        # Determine content type based on file extension
        file_ext = file_path_obj.suffix.lower()
        
        content_type = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.md': 'text/markdown',
            '.txt': 'text/plain'
        }.get(file_ext, 'application/octet-stream')
        
        filename = file_path_obj.name
        files = {'file': (filename, f, content_type)}
        
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        
        return response.json()


def upload_directory(base_url: str, directory_path: str, api_key=None):
    """Upload all supported files from a directory."""
    console = Console()
    document_paths = find_documents(directory_path)
    
    if not document_paths:
        console.print("[yellow]No documents found with supported extensions (.pdf, .docx, .md, .txt)[/yellow]")
        return {}
    
    console.print(f"[green]Found {len(document_paths)} documents[/green]")
    
    # Create a table to track upload progress
    table = Table(title="Document Upload Progress")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Document ID")
    
    uploaded_docs = {}
    
    # Upload each document and record its ID
    for doc_path in document_paths:
        file_name = Path(doc_path).name
        try:
            result = upload_file(base_url, doc_path, api_key)
            doc_id = result.get('id')
            if doc_id:
                uploaded_docs[doc_path] = doc_id
                table.add_row(file_name, "[green]Success[/green]", doc_id)
            else:
                table.add_row(file_name, "[red]Failed[/red]", "N/A")
        except Exception as e:
            table.add_row(file_name, f"[red]Error: {str(e)[:50]}...[/red]", "N/A")
    
    console.print(table)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"uploaded_files_{timestamp}.json"
    
    # Only save the document IDs to a file if we successfully uploaded any documents
    if uploaded_docs:
        with open(output_file, 'w') as f:
            json.dump(uploaded_docs, f, indent=2)
        console.print(f"[green]Document IDs saved to {output_file}[/green]")
    else:
        console.print("[yellow]No documents were successfully uploaded, skipping file creation[/yellow]")
    
    return uploaded_docs


def main():
    """Main function to parse arguments and upload files."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API URL and key from environment
    rag_api_url = os.getenv("RAG_API_URL")
    rag_api_key = os.getenv("RAG_API_KEY")
    
    # Ensure we have the required environment variables
    if not rag_api_url:
        print("Error: RAG_API_URL not set in environment or .env file")
        return 1
    
    parser = argparse.ArgumentParser(description='Upload files to the RAG API')
    parser.add_argument('--dir', default='./test-data',
                        help='Directory containing files to upload (default: ./test-data)')
    parser.add_argument('--file', '-f', help='Upload a single file instead of a directory')
    
    args = parser.parse_args()
    
    console = Console()
    
    try:
        if args.file:
            # Upload a single file
            result = upload_file(rag_api_url, args.file, rag_api_key)
            
            # Create a table to show the result
            table = Table(title="File Upload Result")
            table.add_column("File")
            table.add_column("Status")
            table.add_column("Document ID")
            
            file_name = Path(args.file).name
            doc_id = result.get('id')
            if doc_id:
                table.add_row(file_name, "[green]Success[/green]", doc_id)
                
                # Save the document ID to the output file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"uploaded_files_{timestamp}.json"
                
                with open(output_file, 'w') as f:
                    json.dump({args.file: doc_id}, f, indent=2)
                
                console.print(f"[green]Document ID saved to {output_file}[/green]")
            else:
                table.add_row(file_name, "[red]Failed[/red]", "N/A")
            
            console.print(table)
        else:
            # Upload all files in the directory
            upload_directory(rag_api_url, args.dir, rag_api_key)
    
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            console.print(f"[dim]Response: {e.response.text}[/dim]")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())