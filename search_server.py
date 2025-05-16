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

zip_path = os.path.join(os.path.dirname(__file__), 'data', 'search_index.zip')
search_engine = Search(zip_path)

def convert_sets_to_lists(obj):
    """
    Recursively converts sets to lists within a data structure.
    """
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    if isinstance(obj, dict):
        return {k: convert_sets_to_lists(v) for k, v in obj.items()}
    return obj

@app.route('/search', methods=['GET'])
def search():
    app.logger.info(f"Search request received. Origin: {request.headers.get('Origin')}") # Log the Origin header
    query = request.args.get('q', '')
    if not query:
        app.logger.warning("Search request with no query.")
        return jsonify({"error": "No query provided"}), 400
    try:
        results = search_engine.search(query)
        print(f"Search results: {results}")  # Debugging line
        serializable_results = convert_sets_to_lists(results)
        return jsonify(serializable_results), 200
    except Exception as e:
        app.logger.error(f"Error processing search request: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/summary', methods=['GET'])
def summary():
    app.logger.info(f"Summary request received. Origin: {request.headers.get('Origin')}") # Log the Origin header
    site_id = request.args.get('id', '')
    if not site_id:
        app.logger.warning("Summary request with no site_id.")
        return jsonify({"error": "No site_id provided"}), 400
    try:
        summary_data = search_engine.get_summary(site_id)
        if summary_data is None:
            return jsonify({"error": "Site ID not found"}), 404
        serializable_summary_data = convert_sets_to_lists(summary_data)
        return jsonify(serializable_summary_data), 200
    except Exception as e:
        app.logger.error(f"Error processing summary request: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

#def main():
#    app.run(host='0.0.0.0', port=5000, debug=True)