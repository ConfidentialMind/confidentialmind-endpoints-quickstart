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


def check_connection(base_url: str, api_key=None):
    """Simple connection check to the RAG API."""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        # Try to connect to the base URL
        response = requests.get(base_url, headers=headers, timeout=5)
        return response.status_code >= 200 and response.status_code < 300, response.status_code
    except requests.exceptions.RequestException as e:
        return False, str(e)


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
    
    # Create an error table to show full error details
    error_table = Table(title="Upload Errors")
    error_table.add_column("File")
    error_table.add_column("Error Details")
    
    uploaded_docs = {}
    has_errors = False
    
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
                error_table.add_row(file_name, "No document ID returned")
                has_errors = True
        except Exception as e:
            table.add_row(file_name, "[red]Failed[/red]", "N/A")
            
            # Generate detailed error message
            error_message = str(e)
            if hasattr(e, 'response') and e.response:
                error_message += f"\nStatus code: {e.response.status_code}"
                try:
                    # Try to parse response as JSON
                    error_json = e.response.json()
                    error_message += f"\nResponse: {json.dumps(error_json, indent=2)}"
                except:
                    # Otherwise show text response
                    error_message += f"\nResponse: {e.response.text}"
            
            error_table.add_row(file_name, error_message)
            has_errors = True
    
    console.print(table)
    
    # Display error table if there were errors
    if has_errors:
        console.print(error_table)
    
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
    
    # Check connection to the API first
    is_connected, status = check_connection(rag_api_url, rag_api_key)
    if not is_connected:
        console.print(f"[bold red]Connection to the RAG API failed: {status}[/bold red]")
        return 1
    
    try:
        if args.file:
            # Upload a single file
            try:
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
                
            except Exception as e:
                console.print(f"[bold red]Error uploading file:[/bold red]")
                
                # Show detailed error information
                error_message = str(e)
                if hasattr(e, 'response') and e.response:
                    console.print(f"Status code: {e.response.status_code}")
                    try:
                        # Try to parse response as JSON
                        error_json = e.response.json()
                        console.print("Response:")
                        console.print_json(json.dumps(error_json))
                    except:
                        # Otherwise show text response
                        console.print(f"Response: {e.response.text}")
                else:
                    console.print(error_message)
                    
                return 1
        else:
            # Upload all files in the directory
            upload_directory(rag_api_url, args.dir, rag_api_key)
    
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            console.print(f"Response: {e.response.text}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())