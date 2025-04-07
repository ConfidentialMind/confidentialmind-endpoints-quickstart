#!/usr/bin/env python3
"""
Simple example of deleting files from the RAG API.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table


def delete_file(base_url: str, file_id: str, api_key=None):
    """Delete a file from the RAG system."""
    url = f"{base_url}/files/{file_id}"
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def delete_files_from_json(base_url: str, json_file: str, skip_confirmation=False, api_key=None):
    """Delete files using IDs stored in a JSON file."""
    console = Console()
    
    # Load document IDs from file
    try:
        with open(json_file, 'r') as f:
            uploaded_docs = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File '{json_file}' not found[/red]")
        return {}
    except json.JSONDecodeError:
        console.print(f"[red]Error: File '{json_file}' is not a valid JSON file[/red]")
        return {}
    
    # Extract document IDs and display what will be deleted
    file_ids = list(uploaded_docs.values())
    doc_paths = list(uploaded_docs.keys())
    
    console.print(f"[green]Found {len(file_ids)} files to delete:[/green]")
    for i, (path, file_id) in enumerate(zip(doc_paths, file_ids)):
        console.print(f"  {i+1}. [cyan]{Path(path).name}[/cyan] (ID: {file_id})")
    
    # Confirm deletion if needed
    if not skip_confirmation and len(file_ids) > 0:
        if not Confirm.ask(f"Delete {len(file_ids)} files?"):
            console.print("[yellow]Deletion cancelled[/yellow]")
            return {}
    
    # Create a table to track deletion progress
    table = Table(title="File Deletion Progress")
    table.add_column("File")
    table.add_column("ID")
    table.add_column("Status")
    
    results = {}
    
    # Delete each file
    for path, file_id in zip(doc_paths, file_ids):
        file_name = Path(path).name
        
        try:
            result = delete_file(base_url, file_id, api_key)
            success = result.get('success', False)
            results[file_id] = success
            
            if success:
                table.add_row(file_name, file_id, "[green]Success[/green]")
            else:
                message = result.get('message', 'Unknown error')
                table.add_row(file_name, file_id, f"[red]Failed: {message}[/red]")
        except Exception as e:
            results[file_id] = False
            table.add_row(file_name, file_id, f"[red]Error: {str(e)[:50]}...[/red]")
    
    console.print(table)
    
    # Update the JSON file to remove successfully deleted documents
    if any(results.values()):
        updated_docs = {}
        for path, file_id in uploaded_docs.items():
            if not results.get(file_id, False):
                updated_docs[path] = file_id
        
        if updated_docs:
            with open(json_file, 'w') as f:
                json.dump(updated_docs, f, indent=2)
            console.print(f"[yellow]Updated {json_file} with remaining {len(updated_docs)} files[/yellow]")
        else:
            # All documents were deleted, so remove the file
            try:
                os.remove(json_file)
                console.print(f"[green]All files deleted. Removed {json_file}[/green]")
            except FileNotFoundError:
                pass
    
    return results


def delete_all_from_json_files(base_url: str, skip_confirmation=False, api_key=None):
    """Delete files using IDs stored in all uploaded_files_*.json files."""
    console = Console()
    
    # Find all uploaded_files_*.json files
    json_files = [f for f in Path('.').glob('uploaded_files_*.json') if f.is_file()]
    
    if not json_files:
        console.print("[yellow]No uploaded_files_*.json files found in the current directory.[/yellow]")
        return {'files_found': 0, 'deleted': 0, 'failed': 0}
    
    console.print(f"[green]Found {len(json_files)} JSON files with file IDs.[/green]")
    
    # Collect all file IDs
    all_file_ids = {}  # Map from file_id to (filename, json_file)
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                uploaded_docs = json.load(f)
                
                for path, file_id in uploaded_docs.items():
                    # Store the file name and json file that contains this ID
                    all_file_ids[file_id] = (Path(path).name, json_file)
                    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            console.print(f"[yellow]Warning: Could not process {json_file}: {str(e)}[/yellow]")
    
    # Display summary
    if not all_file_ids:
        console.print("[yellow]No file IDs found in the JSON files.[/yellow]")
        return {'files_found': len(json_files), 'deleted': 0, 'failed': 0}
        
    console.print(f"[green]Found {len(all_file_ids)} unique file IDs to delete.[/green]")
    
    # Confirm deletion if needed
    if not skip_confirmation:
        if not Confirm.ask(f"Delete all {len(all_file_ids)} files?"):
            console.print("[yellow]Deletion cancelled.[/yellow]")
            return {'files_found': len(json_files), 'deleted': 0, 'failed': 0}
    
    # Create a table to track deletion progress
    table = Table(title="File Deletion Progress")
    table.add_column("File")
    table.add_column("ID")
    table.add_column("Status")
    
    statistics = {
        'files_found': len(json_files),
        'deleted': 0,
        'failed': 0
    }
    
    # Process deletions
    for file_id, (file_name, _) in all_file_ids.items():
        try:
            result = delete_file(base_url, file_id, api_key)
            success = result.get('success', False)
            
            if success:
                statistics['deleted'] += 1
                table.add_row(file_name, file_id, "[green]Success[/green]")
            else:
                statistics['failed'] += 1
                message = result.get('message', 'Unknown error')
                table.add_row(file_name, file_id, f"[red]Failed: {message}[/red]")
        except Exception as e:
            statistics['failed'] += 1
            table.add_row(file_name, file_id, f"[red]Error: {str(e)[:50]}...[/red]")
    
    console.print(table)
    
    # Update or delete the JSON files
    for json_file in json_files:
        try:
            os.remove(json_file)
            console.print(f"[green]Removed {json_file}[/green]")
        except Exception as e:
            console.print(f"[yellow]Could not remove {json_file}: {str(e)}[/yellow]")
    
    console.print(f"[green]Summary: {statistics['deleted']} files deleted, {statistics['failed']} failed[/green]")
    
    return statistics


def main():
    """Main function to parse arguments and delete files."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API URL and key from environment
    rag_api_url = os.getenv("RAG_API_URL")
    rag_api_key = os.getenv("RAG_API_KEY")
    
    # Ensure we have the required environment variables
    if not rag_api_url:
        print("Error: RAG_API_URL not set in environment or .env file")
        return 1
    
    parser = argparse.ArgumentParser(description='Delete files from the RAG API')
    parser.add_argument('--id', help='Delete a single file by ID')
    parser.add_argument('--from-json', '-j', help='Delete files listed in a JSON file')
    parser.add_argument('--all', '-a', action='store_true', 
                        help='Delete all files from all uploaded_files_*.json files')
    parser.add_argument('--yes', '-y', action='store_true', 
                        help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Check if at least one deletion method is specified
    if not (args.id or args.from_json or args.all):
        parser.error("Please specify either --id, --from-json, or --all")
    
    console = Console()
    
    try:
        if args.id:
            # Confirm deletion if needed
            if not args.yes:
                if not Confirm.ask(f"Delete file with ID '{args.id}'?"):
                    console.print("[yellow]Deletion cancelled[/yellow]")
                    return 0
            
            # Delete a single file
            result = delete_file(rag_api_url, args.id, rag_api_key)
            
            if result.get('success', False):
                console.print(f"[green]Successfully deleted file with ID: {args.id}[/green]")
            else:
                message = result.get('message', 'Unknown error')
                console.print(f"[red]Failed to delete file: {message}[/red]")
        
        elif args.from_json:
            # Delete files from JSON file
            delete_files_from_json(rag_api_url, args.from_json, args.yes, rag_api_key)
            
        elif args.all:
            # Delete all files from all JSON files
            delete_all_from_json_files(rag_api_url, args.yes, rag_api_key)
    
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            console.print(f"[dim]Response: {e.response.text}[/dim]")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())