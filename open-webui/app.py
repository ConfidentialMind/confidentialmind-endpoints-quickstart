import os
import json
import requests
from flask import Flask, request, Response, jsonify, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variable to store endpoint configurations
endpoints = {}

def load_endpoints_from_json(config_file='config.json'):
    """Load endpoint configurations from a JSON file"""
    global endpoints
    
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            endpoints = config_data.get('endpoints', {})
        
        if not endpoints:
            print(f"Warning: No endpoints found in {config_file}")
            return False
        
        # Log loaded endpoints
        for model_id, config in endpoints.items():
            print(f"Loaded endpoint: {model_id} ({config.get('displayName', 'unnamed')})")
        
        return True
    except FileNotFoundError:
        print(f"Error: Configuration file {config_file} not found.")
        return False
    except json.JSONDecodeError:
        print(f"Error: Configuration file {config_file} contains invalid JSON.")
        return False
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False

@app.route('/models', methods=['GET'])
def list_models():
    """Handle model listing with custom display names"""
    try:
        models = []
        for model_id, config in endpoints.items():
            models.append({
                "id": model_id,
                "object": "model",
                "created": 1677610602,  # Placeholder timestamp
                "owned_by": config.get("displayName", model_id),
                "permission": [{
                    "id": "modelperm",
                    "object": "model_permission",
                    "created": 1677610602,
                    "allow_create_engine": False,
                    "allow_sampling": True,
                    "allow_logprobs": True,
                    "allow_search_indices": False,
                    "allow_view": True,
                    "allow_fine_tuning": False,
                    "organization": "*",
                    "group": None,
                    "is_blocking": False
                }]
            })

        return jsonify({
            "object": "list",
            "data": models
        })
    except Exception as e:
        print(f"Error in /v1/models: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    """Handle chat completions with model name replacement"""
    try:
        data = request.json
        model_name = data.get('model')
        
        if not model_name or model_name not in endpoints:
            return jsonify({
                "error": f"Model '{model_name}' not supported. Available models: {', '.join(endpoints.keys())}"
            }), 400
        
        endpoint_config = endpoints[model_name]
        
        # Replace the model name with the actual backend model name
        modified_data = data.copy()
        modified_data['model'] = endpoint_config.get('actualModelName', 'cm-llm')
        
        headers = {
            'Authorization': f"Bearer {endpoint_config.get('apiKey', '')}",
            'Content-Type': 'application/json'
        }

        # Ensure proper URL joining by handling trailing slashes
        base_url = endpoint_config.get('url', '').rstrip('/')

        # Handle streaming responses
        if data.get('stream', False):
            def generate():
                response = requests.post(
                    f"{base_url}/v1/chat/completions",
                    json=modified_data,
                    headers=headers,
                    stream=True
                )
                
                # Stream the response directly to the client
                for chunk in response.iter_lines():
                    if chunk:
                        yield chunk + b'\n'

            return Response(
                stream_with_context(generate()),
                content_type='text/event-stream'
            )
        else:
            # Handle non-streaming responses
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json=modified_data,
                headers=headers
            )
            
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/json')
            )
    except Exception as e:
        print(f"Error in /v1/chat/completions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "ok",
        "endpoints": len(endpoints),
        "models": [{"id": id, "displayName": config.get("displayName", id)} for id, config in endpoints.items()]
    })


@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(subpath):
    """Generic proxy handler for all other routes"""
    try:
        # Determine which model/endpoint to use
        model_id = request.headers.get('x-model-id')
        
        if not model_id:
            if request.method == 'GET':
                model_id = request.args.get('model')
            else:
                data = request.get_json(silent=True) or {}
                model_id = data.get('model')
        
        if not model_id or model_id not in endpoints:
            return jsonify({
                "error": f"Missing or invalid model ID. Please specify a valid model ID. Available models: {', '.join(endpoints.keys())}"
            }), 400
        
        endpoint_config = endpoints[model_id]
        
        # Prepare headers
        headers = dict(request.headers)
        headers['Authorization'] = f"Bearer {endpoint_config.get('apiKey', '')}"
        
        # Remove host header to avoid conflicts
        if 'Host' in headers:
            del headers['Host']
        
        # Ensure proper URL joining by handling trailing slashes
        base_url = endpoint_config.get('url', '').rstrip('/')
        url = f"{base_url}/v1/{subpath}"
        
        # Prepare data based on method
        data = None
        params = None
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = request.get_json(silent=True) or {}
            # Replace model name if present
            if data.get('model') == model_id:
                data['model'] = endpoint_config.get('actualModelName', 'cm-llm')
        
        if request.args:
            params = dict(request.args)
            # Replace model name in query params if present
            if params.get('model') == model_id:
                params['model'] = endpoint_config.get('actualModelName', 'cm-llm')
        
        # Make the actual request to the backend
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params if params else None,
            stream=True
        )
        
        # Check if it's a streaming response
        is_stream = 'text/event-stream' in response.headers.get('Content-Type', '')
        
        if is_stream:
            def generate():
                for chunk in response.iter_lines():
                    if chunk:
                        yield chunk + b'\n'
            
            return Response(
                stream_with_context(generate()),
                content_type='text/event-stream'
            )
        else:
            # For non-streaming responses
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/json')
            )
    except Exception as e:
        print(f"Error in proxy_request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/debug', methods=['GET'])
def debug_info():
    """Endpoint to show configuration details for debugging"""
    # Only show partial API keys for security
    safe_endpoints = {}
    for id, config in endpoints.items():
        api_key = config.get("apiKey", "")
        masked_key = api_key[:5] + "..." + api_key[-5:] if len(api_key) > 10 else "***"
        
        safe_endpoints[id] = {
            "displayName": config.get("displayName", id),
            "url": config.get("url", ""),
            "apiKey": masked_key,
            "actualModelName": config.get("actualModelName", "cm-llm")
        }
    
    return jsonify({
        "endpoints": safe_endpoints,
        "config_file_location": os.path.abspath("config.json")
    })

@app.route('/reload', methods=['POST'])
def reload_config():
    """Endpoint to reload configuration file"""
    config_file = request.args.get('config', 'config.json')
    success = load_endpoints_from_json(config_file)
    
    if success:
        return jsonify({
            "status": "ok",
            "message": f"Configuration reloaded from {config_file}",
            "endpoints": len(endpoints),
            "models": list(endpoints.keys())
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Failed to reload configuration from {config_file}"
        }), 500

if __name__ == '__main__':
    # Load configuration file
    config_file = os.environ.get('CM_OPEN_WEBUI_PROXY_CONFIG_FILE', 'config.json')
    if not load_endpoints_from_json(config_file):
        print(f"Using example configuration")
        # Provide an example configuration
        endpoints = {
            'model-instance-1': {
                "displayName": 'Model Instance 1',
                "url": 'https://endpoint1.com',
                "apiKey": 'key1',
                "actualModelName": 'cm-llm'
            }
        }
    
    port = int(os.environ.get('CM_OPEN_WEBUI_PROXY_PORT', 3333))
    print(f"OpenAI compatible multi-endpoint proxy running on port {port}")
    print(f"Available models: {', '.join(endpoints.keys())}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Debug info: http://localhost:{port}/debug")
    app.run(host='0.0.0.0', port=port, debug=True)