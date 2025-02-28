from flask import Flask, request, jsonify
from search import Search
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/search": {"origins": "*"}})

# Initialize search engine
search_engine = Search()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    return search_engine.get_formatted_results(query, jsonify)

def main():
    app.run(host='localhost', port=5000, debug=True)

if __name__ == '__main__':
    main()
