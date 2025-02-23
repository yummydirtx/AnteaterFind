#from file import FileOpener
from index import InvertedIndex
import os

def generate_m1_report():
    index = InvertedIndex(r"zips/developer.zip") #test
    numDocuments = index.total_documents
    uniqueTokens = index.get_unique_tokens()
    numUniqueTokens = len(uniqueTokens)

    with open("M1Report.txt", 'w') as f:
        f.write(f"The number of indexed documents: {numDocuments}\n")
        f.write(f"The number of unique words: {numUniqueTokens}\n")
        index_size = os.path.getsize("index.json") / 1024  # Convert bytes to KB
        f.write(f"The total size (in KB) of index on disk: {index_size:.2f}\n")

if __name__ == "__main__":
    generate_m1_report()
