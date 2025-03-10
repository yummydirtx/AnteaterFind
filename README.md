![AnteaterFind logo](search-frontend/public/anteaterfind.png)

# AnteaterFind

AnteaterFind is a full stack web application and indexer, written using Python and React. AnteaterFind was written from the ground up, and is capable of handling over fifty thousand web pages, with a query response time under 300ms.

## Features

- **Memory light**:
    - The indexer is designed to never load the entire index into memory at once, making it ideal for large sets of files.
    - The search module reads tokens from the index one at a time, never loading the entire index into memory at once.

- **Fast query response time**:
    - The indexer keeps an index of token positions in the index, allowing O(1) token lookup at search time
    - When retrieving documents, the search module uses an optimized order to avoid retrieving unnecessary results for the boolean AND query.

- **Elegant web frontend**:
    - The lightweight React frontend delegates search tasks to HTML GET requests from the Python backend, allowing for a simple design
    - There are animations for most search functions, improving user experience

- **ChatGPT summaries**:
    - Provided an OpenAI api key, the search module uses ChatGPT to summarize retrieved web pages.
    - ChatGPT summarization occurs after query retrieval, preventing potential slowdown

## Installation and Usage

### Prerequisites

- Python 3.9 or higher
- `pip` package manager
- `npm` package manager

### Install Dependencies

To install the Python dependencies for this project, clone the repository and install the requirements:

```bash
# Clone the repository
git clone https://github.com/yummydirtx/AnteaterFind.git
cd AnteaterFind

# Install the Python dependencies
pip install -r requirements.txt
```

To install the React dependencies for this project, simply change directories to the `search-frontend` folder and run `npm install` to find and install the dependencies:

```bash
# Change to the frontend directory
cd search-frontend

# Install npm dependencies
npm install
```

### Indexing

Run the indexer from your command line:

```bash
# Change your directory to the base directory, if it isn't there already
# Replace the path with the path to your zip containing the documents to index
python start_index.py path/to/documents.zip

# To run the indexer with simhash to eliminate similar documents use:
python start_index.py path/to/documents.zip -s
```

### Search

To run the Search component, two separate terminals are needed to run the backend and the frontend. To run the backend, open the first terminal:

```bash
# Run the backend with no ChatGPT summaries
python search_server.py

# Optional: run the backend with ChatGPT summaries
# Replace placeholder parameters
python search_server.py path/to/documents.zip OPENAI-API-KEY
```

Leave this terminal running and open a second terminal to run the frontend:

```bash
# Start the npm server
cd search-frontend
npm start
```

Open a web browser and navigate to [localhost](localhost:3000) to view and use the search engine.

## Attribution

The logo of an Anteater with a magnifying glass over it was generated by DALL-E.