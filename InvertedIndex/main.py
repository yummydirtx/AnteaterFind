#from file import FileOpener
from index import InvertedIndex
import os
import sys

def generate_m1_report(path: str):
    """
    Generates a report containing index statistics.
    Args:
        path: Path to the document collection
    Creates:
        M1Report.txt containing:
        - Number of indexed documents
        - Number of unique words
        - Total size of index on disk
    """
    index = InvertedIndex(path)
    numDocuments = index.total_documents
    numUniqueTokens = index.unique_tokens()

    with open("M1Report.txt", 'w') as f:
        f.write(f"The number of indexed documents: {numDocuments}\n")
        f.write(f"The number of unique words: {numUniqueTokens}\n")
        index_size = os.path.getsize("index.json") / 1024  # Convert bytes to KB
        url_map_size = os.path.getsize("urls.json") / 1024  # Convert bytes to KB
        total_size = index_size + url_map_size
        f.write(f"The total size (in KB) of index on disk: {total_size:.2f}\n")

def generate_index(path: str):
    """
    Generates an inverted index from the document collection, without creating a report.
    Args:
        path : Path to the document collection
    Creates:
        index.json, urls.json, and token_positions.json
    """
    InvertedIndex(path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_documents>")
        sys.exit(1)
    generate_m1_report(sys.argv[1])
