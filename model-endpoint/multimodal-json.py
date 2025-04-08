#!/usr/bin/env python
"""
Example of using multimodal capabilities with guided JSON output.
This demonstrates how to extract structured data from images.
"""

import os
import base64
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv

# Sample JSON schema for document/image analysis
# Note: This is a simple example - schema capabilities have some limitations
DOCUMENT_SCHEMA = {
  "type": "object",
  "properties": {
    "document": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "content": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {"type": "string"},
              "text": {"type": "string"},
              "items": {"type": "array", "items": {"type": "string"}},
              "headers": {"type": "array", "items": {"type": "string"}},
              "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
              "description": {"type": "string"}
            }
          }
        },
        "metadata": {
          "type": "object",
          "properties": {
            "has_tables": {"type": "boolean"},
            "has_images": {"type": "boolean"}
          }
        }
      },
      "required": ["content"]
    }
  },
  "required": ["document"]
}

def encode_image(image_path):
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_content_type(file_path):
    """Determine content type based on file extension."""
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.png':
        return 'image/png'
    elif extension in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    elif extension == '.gif':
        return 'image/gif'
    elif extension == '.webp':
        return 'image/webp'
    else:
        # Default to png if unknown
        return 'image/png'

def main():
    parser = argparse.ArgumentParser(description='Extract structured data from images using our API')
    parser.add_argument('--image', type=str, default='test-data/image_table.png',
                        help='Path to image file (default: test-data/image_table.png)')
    parser.add_argument('--output', type=str, default='output.json',
                        help='Path to save the output JSON (default: output.json)')
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API credentials from environment variables
    # Note that the model deployed in the API must support multimodal capabilities
    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL_NAME", "cm-llm")
    
    # Verify credentials are available
    if not base_url or not api_key:
        print("Error: BASE_URL and API_KEY must be set in .env file")
        return
    
    # Ensure base_url ends with /v1
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    
    # Check if image file exists
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        return
    
    # Initialize the OpenAI client with our API endpoint
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    
    # Encode the image to base64
    try:
        base64_image = encode_image(args.image)
        content_type = get_content_type(args.image)
    except Exception as e:
        print(f"Error encoding image: {e}")
        return
    
    # Prepare the messages with image
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the content of this image as structured data. "
                                         "Identify any text, tables, lists, and other elements."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content_type};base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    print(f"Processing image: {args.image}")
    print("Requesting structured JSON extraction...")
    
    # Make the API request with guided JSON output
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=3000,
            extra_body={
                "guided_json": DOCUMENT_SCHEMA,
                "guided_decoding_backend": "xgrammar"  # This backend is used for decoding
            }
        )
        
        # Extract and parse the response
        json_response = response.choices[0].message.content
        
        # Display the raw JSON response
        print("\nRaw JSON Response:")
        print("-" * 60)
        print(json_response)
        print("-" * 60)
        
        # Parse and save the JSON
        try:
            parsed_json = json.loads(json_response)
            
            # Save to file
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, indent=2)
            print(f"\nStructured data saved to: {args.output}")
            
            # Display summary
            document = parsed_json.get("document", {})
            content = document.get("content", [])
            
            print("\nExtracted Content Summary:")
            content_types = {}
            for item in content:
                item_type = item.get("type", "unknown")
                content_types[item_type] = content_types.get(item_type, 0) + 1
            
            for content_type, count in content_types.items():
                print(f"  - {content_type}: {count} items")
            
        except json.JSONDecodeError:
            print("Error: The response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nNote: Our guided JSON capabilities have some limitations.")
    print("For complex schemas or special requirements, please contact our support team.")

if __name__ == "__main__":
    main()