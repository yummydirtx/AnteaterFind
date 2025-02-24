#from file import FileOpener
from index import InvertedIndex
import os
import sys

def generate_m1_report(path: str):
    index = InvertedIndex(path) #test
    numDocuments = index.total_documents
    numUniqueTokens = index.get_unique_tokens()

    with open("M1Report.txt", 'w') as f:
        f.write(f"The number of indexed documents: {numDocuments}\n")
        f.write(f"The number of unique words: {numUniqueTokens}\n")
        index_size = os.path.getsize("index.json") / 1024  # Convert bytes to KB
        f.write(f"The total size (in KB) of index on disk: {index_size:.2f}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_documents>")
        sys.exit(1)
    generate_m1_report(sys.argv[1])
