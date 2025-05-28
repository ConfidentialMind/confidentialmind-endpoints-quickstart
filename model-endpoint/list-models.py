#!/usr/bin/env python3
"""
Example: List available models from the endpoint

This example demonstrates how to retrieve and display available models.
For model endpoints, this will show all configured models.
For direct deployments, this typically shows only 'cm-llm'.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

if not BASE_URL or not API_KEY:
    print("Error: Please set BASE_URL and API_KEY in your .env file")
    exit(1)

# Construct the models endpoint URL
models_url = f"{BASE_URL}/v1/models"
print(f"Using models endpoint: {models_url}")

# Set up headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    print(f"Fetching models from: {models_url}")
    response = requests.get(models_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("data", [])
        
        print(f"\n✅ Found {len(models)} available model(s):")
        print("-" * 50)
        
        for i, model in enumerate(models, 1):
            model_id = model.get("id", "Unknown")
            created = model.get("created", "Unknown")
            owned_by = model.get("owned_by", "Unknown")
            
            print(f"{i}. Model ID: {model_id}")
            print(f"   Created: {created}")
            print(f"   Owned by: {owned_by}")
            print()
        
        # Provide guidance based on number of models
        if len(models) == 1 and models[0].get("id") == "cm-llm":
            print("💡 This appears to be a direct model deployment.")
            print("   Use 'cm-llm' as the model name in your requests.")
        elif len(models) > 1:
            print("💡 This appears to be a model endpoint with multiple models.")
            print("   You can specify any of the above model IDs in your requests.")
        else:
            print("💡 No models found or endpoint configuration may need review.")
            
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        
        if response.status_code == 401:
            print("   Check your API key in the .env file")
        elif response.status_code == 404:
            print("   Check your BASE_URL in the .env file")
        elif response.status_code == 403:
            print("   Your API key may not have permission to list models")

except requests.exceptions.ConnectionError:
    print("❌ Connection error: Could not connect to the endpoint")
    print("   Check your BASE_URL and network connectivity")
except requests.exceptions.Timeout:
    print("❌ Request timeout: The endpoint took too long to respond")
except Exception as e:
    print(f"❌ Unexpected error: {e}")