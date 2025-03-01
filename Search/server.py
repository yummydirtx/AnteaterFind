from flask import Flask, request, jsonify
from search import Search
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS more explicitly to handle both localhost and 127.0.0.1
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

# Initialize search engine
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

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)  # Changed host to 0.0.0.0 to listen on all interfaces

if __name__ == '__main__':
    main()
