#!/usr/bin/env python3
"""
Advanced example of uploading files to the RAG API with all supported parameters.

This example demonstrates:
- Uploading files with custom metadata
- Setting user_id for organization/permissions
- Using document_id for custom identifiers
- Organizing files with group_ids
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


def upload_file_advanced(
    base_url: str, 
    file_path: str, 
    user_id=None,
    document_id=None,
    group_ids=None,
    metadata=None,
    api_key=None
):
    """
    Upload a single file to the RAG system with advanced parameters.
    
    Args:
        base_url: Base URL of the RAG API
        file_path: Path to the file to upload
        user_id: Optional user ID to associate with the file
        document_id: Optional custom ID for the document
        group_ids: Optional list of group IDs to associate with the file
        metadata: Optional dictionary of metadata to associate with the file
        api_key: API key for authentication
        
    Returns:
        Response JSON from the API
    """
    url = f"{base_url}/files"
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine content type based on file extension
    file_ext = file_path_obj.suffix.lower()
    content_type = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.md': 'text/markdown',
        '.txt': 'text/plain'
    }.get(file_ext, 'application/octet-stream')
    
    # Prepare the file data
    filename = file_path_obj.name
    
    with open(file_path, 'rb') as f:
        files = {'file': (filename, f, content_type)}
        
        # Prepare form data for additional parameters
        data = {}
        if user_id:
            data['user_id'] = user_id
        if document_id:
            data['document_id'] = document_id
        if group_ids:
            # Handle group_ids as a list or comma-separated string
            if isinstance(group_ids, list):
                # For requests library, we need to provide multiple values
                # with the same key for array parameters
                for group_id in group_ids:
                    data['group_ids'] = group_id
            else:
                # If it's a comma-separated string, split it
                for group_id in group_ids.split(','):
                    data['group_ids'] = group_id.strip()
        if metadata:
            # Convert metadata to JSON string if it's a dictionary
            if isinstance(metadata, dict):
                data['metadata'] = json.dumps(metadata)
            else:
                data['metadata'] = metadata
        
        # Make the request
        response = requests.post(url, files=files, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()


def upload_directory_advanced(
    base_url: str, 
    directory_path: str, 
    user_id=None,
    group_ids=None,
    metadata_template=None,
    api_key=None
):
    """
    Upload all supported files from a directory with advanced parameters.
    
    Args:
        base_url: Base URL of the RAG API
        directory_path: Path to directory containing files to upload
        user_id: Optional user ID to associate with all files
        group_ids: Optional list of group IDs for all files
        metadata_template: Optional dictionary of metadata to use as a template
        api_key: API key for authentication
        
    Returns:
        Dictionary mapping file paths to document IDs
    """
    console = Console()
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Find all supported document files
    allowed_extensions = {'.pdf', '.docx', '.md', '.txt'}
    document_paths = [
        str(file_path.absolute())
        for file_path in directory.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions
    ]
    
    if not document_paths:
        console.print("[yellow]No documents found with supported extensions (.pdf, .docx, .md, .txt)[/yellow]")
        return {}
    
    console.print(f"[green]Found {len(document_paths)} documents[/green]")
    
    # Create a table to track upload progress
    table = Table(title="Document Upload Progress")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Document ID")
    table.add_column("User ID")
    table.add_column("Group IDs")
    
    # Create an error table to show full error details
    error_table = Table(title="Upload Errors")
    error_table.add_column("File")
    error_table.add_column("Error Details")
    
    uploaded_docs = {}
    has_errors = False
    
    # Upload each document and record its ID
    for doc_path in document_paths:
        file_name = Path(doc_path).name
        
        # Generate file-specific metadata by extending the template
        metadata = None
        if metadata_template:
            metadata = metadata_template.copy()
            # Add filename to metadata if template exists
            if isinstance(metadata, dict):
                metadata['filename'] = file_name
        
        try:
            result = upload_file_advanced(
                base_url=base_url,
                file_path=doc_path,
                user_id=user_id,
                group_ids=group_ids,
                metadata=metadata,
                api_key=api_key
            )
            
            doc_id = result.get('id')
            if doc_id:
                uploaded_docs[doc_path] = doc_id
                # Prepare display values for the table
                groups_display = ', '.join(group_ids) if isinstance(group_ids, list) else group_ids
                table.add_row(
                    file_name, 
                    "[green]Success[/green]", 
                    doc_id,
                    user_id or "default",
                    groups_display or "none"
                )
            else:
                table.add_row(file_name, "[red]Failed[/red]", "N/A", user_id or "N/A", "N/A")
                error_table.add_row(file_name, "No document ID returned")
                has_errors = True
        except Exception as e:
            table.add_row(file_name, "[red]Failed[/red]", "N/A", user_id or "N/A", "N/A")
            
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
    
    # Save the document IDs to a file if we successfully uploaded any documents
    if uploaded_docs:
        with open(output_file, 'w') as f:
            json.dump(uploaded_docs, f, indent=2)
        console.print(f"[green]Document IDs saved to {output_file}[/green]")
    else:
        console.print("[yellow]No documents were successfully uploaded, skipping file creation[/yellow]")
    
    return uploaded_docs


def prepare_metadata(metadata_str=None, metadata_file=None):
    """
    Process metadata from string or file.
    
    Args:
        metadata_str: JSON string of metadata
        metadata_file: Path to JSON file containing metadata
        
    Returns:
        Dictionary of metadata
    """
    if metadata_file:
        with open(metadata_file, 'r') as f:
            return json.load(f)
    elif metadata_str:
        return json.loads(metadata_str)
    return None


def main():
    """Main function to parse arguments and upload files with advanced options."""
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
        description='Advanced example: Upload files to the RAG API with all parameters'
    )
    
    # File selection arguments
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Handle running from either /advanced or the root directory
    if os.path.basename(script_dir) == 'advanced':
        default_test_data = os.path.join(os.path.dirname(script_dir), 'test-data')
    else:
        default_test_data = './test-data'
        
    parser.add_argument('--dir', default=default_test_data,
                        help=f'Directory containing files to upload (default: {default_test_data})')
    parser.add_argument('--file', '-f',
                        help='Upload a single file instead of a directory (e.g., test-data/rag-endpoint.md)')
    
    # Advanced parameters
    parser.add_argument('--user-id', default="example-user",
                        help='User ID to associate with the files (default: "example-user")')
    parser.add_argument('--document-id',
                        help='Custom document ID (only for single file uploads, auto-generated if not provided)')
    parser.add_argument('--group-ids', default="documentation",
                        help='Comma-separated list of group IDs (default: "documentation")')
    
    # Add help text to explain filtering capabilities
    metadata_help = '''JSON string of metadata (default: example metadata).
Examples for effective filtering:
  
  # GROUP ID FILTERING (RECOMMENDED):
  --group-ids "whitepaper" for the whitepaper
  --group-ids "api-docs" for the markdown doc
  
  # METADATA FILTERING (OPTIONAL):
  --metadata '{"source": "whitepaper", "department": "Engineering"}' for the whitepaper
  --metadata '{"source": "documentation", "department": "Product"}' for the markdown doc
  
These can later be filtered using the respective parameters in retrieval_advanced.py'''
    
    parser.add_argument('--metadata', 
                        default='{"source": "example", "department": "Engineering", "category": "Documentation"}',
                        help=metadata_help)
    parser.add_argument('--metadata-file',
                        help='Path to JSON file containing metadata')
    
    args = parser.parse_args()
    
    console = Console()
    
    # Process metadata
    metadata = prepare_metadata(args.metadata, args.metadata_file)
    
    # Process group IDs
    group_ids = None
    if args.group_ids:
        group_ids = [g.strip() for g in args.group_ids.split(',') if g.strip()]
    
    try:
        if args.file:
            # Upload a single file with advanced parameters
            console.print(f"[bold]Uploading file with advanced parameters:[/bold]")
            console.print(f"File: {args.file}")
            console.print(f"User ID: {args.user_id}")
            if args.document_id:
                console.print(f"Document ID: {args.document_id}")
            else:
                console.print(f"Document ID: auto-generated")
            console.print(f"Group IDs: {', '.join(group_ids) if group_ids else 'none'}")
            if metadata:
                console.print("Metadata:", metadata)
            
            result = upload_file_advanced(
                base_url=rag_api_url,
                file_path=args.file,
                user_id=args.user_id,
                document_id=args.document_id,
                group_ids=group_ids,
                metadata=metadata,
                api_key=rag_api_key
            )
            
            # Display the result
            console.print("\n[bold green]Upload successful:[/bold green]")
            console.print_json(json.dumps(result))
            
            # Save the document ID to the output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"uploaded_files_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump({args.file: result.get('id')}, f, indent=2)
            
            console.print(f"[green]Document ID saved to {output_file}[/green]")
        else:
            # Upload all files in the directory with advanced parameters
            console.print(f"[bold]Uploading directory with advanced parameters:[/bold]")
            console.print(f"Directory: {args.dir}")
            console.print(f"User ID: {args.user_id}")
            console.print(f"Group IDs: {', '.join(group_ids) if group_ids else 'none'}")
            if metadata:
                console.print("Metadata template:", metadata)
            
            upload_directory_advanced(
                base_url=rag_api_url,
                directory_path=args.dir,
                user_id=args.user_id,
                group_ids=group_ids,
                metadata_template=metadata,
                api_key=rag_api_key
            )
    
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            console.print(f"Response: {e.response.text}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())