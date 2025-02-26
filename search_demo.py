from search import Search
import sys
import time

def main():
    """
    Command-line interface to demonstrate search functionality.
    Also displays timing information to show performance improvements.
    """
    print("Initializing search engine...")
    start_time = time.time()
    search_engine = Search()
    init_time = time.time() - start_time
    print(f"Search engine initialized in {init_time:.2f} seconds")
    
    if len(sys.argv) > 1:
        # Use command line argument as query
        query = ' '.join(sys.argv[1:])
        print(f"Searching for: {query}")
        start_time = time.time()
        results = search_engine.search(query)
        search_time = time.time() - start_time
        print(f"Search completed in {search_time:.2f} seconds")
        search_engine.print_results(results)
    else:
        # Interactive mode
        print("Search Engine Demo")
        print("Type 'exit' to quit")
        
        while True:
            query = input("\nEnter search query: ")
            if query.lower() == 'exit':
                break
                
            start_time = time.time()
            results = search_engine.search(query)
            search_time = time.time() - start_time
            
            search_engine.print_results(results)
            print(f"Search completed in {search_time:.2f} seconds")

if __name__ == "__main__":
    main()
