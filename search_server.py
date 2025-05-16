from flask import Flask, request, jsonify
from Search import Search
from flask_cors import CORS
import sys
import os

app = Flask(__name__)
# Configure CORS more explicitly to handle both localhost and 127.0.0.1
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://34.172.71.18:5000", "http://anteaterfind.com"]}})

# Initialize search engine
if len(sys.argv) > 2:
        zip_path = sys.argv[1]
        api_key = sys.argv[2]
        os.environ["OPENAI_API_KEY"] = api_key
        search_engine = Search(zip_path)
else:
    api_key = os.environ.get("OPENAI_API_KEY")
    zip_path = os.environ.get("DOC_PATH")
    search_engine = Search()

# Add a custom after_request handler to ensure CORS headers are present
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    return search_engine.get_formatted_results(query, jsonify)

@app.route('/summary', methods=['GET'])
def summary():
    site_id = request.args.get('id', '')
    if not site_id:
        return jsonify({'error': 'No URL provided'}), 400
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 400
    return search_engine.get_summary(site_id, api_key, jsonify)

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)  # Changed host to 0.0.0.0 to listen on all interfaces

if __name__ == '__main__':
    main()
