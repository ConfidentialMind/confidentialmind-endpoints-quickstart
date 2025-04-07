#!/usr/bin/env python
"""
Example of using the multimodal capabilities of our API to process images.
This script sends an image to the model and asks for a simple description.
"""

import os
import base64
import argparse
from openai import OpenAI
from dotenv import load_dotenv

def encode_image(image_path):
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description='Get descriptions of images using our multimodal API')
    parser.add_argument('--image', type=str, default='test-data/image.png',
                        help='Path to image file (default: test-data/image.png)')
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API credentials from environment variables
    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL_NAME")  # Should be a multimodal-capable model
    
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
    except Exception as e:
        print(f"Error encoding image: {e}")
        return
    
    # Prepare the messages with image
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please describe what you see in this image."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    print(f"Processing image: {args.image}")
    
    # Make the API request
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        # Extract and print the response
        result = response.choices[0].message.content
        
        print("\nImage Description:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()