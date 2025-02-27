import sys
from InvertedIndex import generate_index

def main():
    """
    Command-line interface to generate an inverted index.
    Usage: python start_index.py <path_to_documents>
    """
    if len(sys.argv) != 2:
        print("Usage: python start_index.py <path_to_documents>")
        sys.exit(1)

    path = sys.argv[1]
    generate_index(path)
    print("Inverted index generated successfully.")

if __name__ == "__main__":
    main()
    