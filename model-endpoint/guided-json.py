#!/usr/bin/env python
"""
Example of using guided JSON output with our API.
This demonstrates how to get structured data from the model using a JSON schema.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Sample JSON schema to guide the model's output
# Note: This is a simple example - schema capabilities have some limitations
SAMPLE_SCHEMA = {
  "type": "object",
  "properties": {
    "analysis": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_points": {
          "type": "array",
          "items": {"type": "string"}
        },
        "sentiment": {
          "type": "string",
          "enum": ["positive", "neutral", "negative"]
        },
        "categories": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["summary", "key_points", "sentiment"]
    }
  },
  "required": ["analysis"]
}

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API credentials from environment variables
    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL_NAME")
    
    # Verify credentials are available
    if not base_url or not api_key:
        print("Error: BASE_URL and API_KEY must be set in .env file")
        return
    
    # Ensure base_url ends with /v1
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    
    # Initialize the OpenAI client with our API endpoint
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    
    # Prepare user prompt that will work well with the JSON schema
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides analysis in structured JSON format."},
        {"role": "user", "content": "Analyze the following text and provide structured insights: "
         "Renewable energy investments hit a record high last quarter, with solar projects "
         "leading the way. Despite supply chain challenges, new installations increased by 28%. "
         "However, regulatory uncertainty in some markets has caused concern among investors."}
    ]
    
    # Create the API request with guided JSON output
    print("Requesting guided JSON response...")
    try:
        # Note: The extra_body parameter is used to pass the JSON schema
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=500,
            extra_body={
                "guided_json": SAMPLE_SCHEMA,
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
        
        # Parse and pretty-print the JSON
        try:
            parsed_json = json.loads(json_response)
            print("\nPretty-printed JSON:")
            print("-" * 60)
            print(json.dumps(parsed_json, indent=2))
            print("-" * 60)
            
            # Example of accessing specific fields
            if "analysis" in parsed_json:
                analysis = parsed_json["analysis"]
                print("\nHighlights from the analysis:")
                print(f"Sentiment: {analysis.get('sentiment', 'N/A')}")
                print(f"Summary: {analysis.get('summary', 'N/A')}")
                
                if "key_points" in analysis:
                    print("\nKey Points:")
                    for i, point in enumerate(analysis["key_points"], 1):
                        print(f"{i}. {point}")
        except json.JSONDecodeError:
            print("Error: The response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nNote: Our guided JSON capabilities have some limitations.")
    print("For complex schemas or special requirements, please contact our support team.")

if __name__ == "__main__":
    main()