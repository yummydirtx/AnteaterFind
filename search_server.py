from flask import Flask, request, jsonify
from Search import Search
from flask_cors import CORS
import sys
import os
import logging # Import the logging module

app = Flask(__name__)
# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Configure CORS more explicitly to handle all routes, origins, methods, and headers
CORS(app, 
     resources={r"/*": { # Apply to all routes under the app
         "origins": ["https://anteaterfind.com", "http://localhost:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Add other methods if needed
         "allow_headers": ["Authorization", "Content-Type"],
         "supports_credentials": True # Explicitly allow credentials
     }})

api_key = os.environ.get("OPENAI_API_KEY")
zip_path = os.environ.get("DOC_PATH")
search_engine = Search(zip_path)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    offset = request.args.get('offset', 0, type=int) # Add offset parameter, default to 0
    limit = request.args.get('limit', 5, type=int) # Add limit parameter, default to 5
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    return search_engine.get_formatted_results(query, jsonify, offset=offset, limit=limit) # Pass offset and limit

@app.route('/summary', methods=['GET'])
def summary():
    site_id = request.args.get('id', '')
    if not site_id:
        return jsonify({'error': 'No URL provided'}), 400
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 400
    return search_engine.get_summary(site_id, api_key, jsonify)

#def main():
#    app.run(host='0.0.0.0', port=5000, debug=True)