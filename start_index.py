import sys
from InvertedIndex import generate_index

def main():
    """
    Command-line interface to generate an inverted index.
    Usage: python start_index.py <path_to_documents>
    """
    if len(sys.argv) < 2:
        print("Usage: python start_index.py <path_to_documents> (optional: -s for simhash indexing)")
        sys.exit(1)

    path = sys.argv[1]
    if '-s' in sys.argv:
        generate_index(path)
    else:
        generate_index(path, sim_hash=0)
    print("Inverted index generated successfully.")

if __name__ == "__main__":
    main()
    