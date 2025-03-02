import json
from .cache import LRUCache

class IndexReader:
    """
    Handles disk-based index reading operations with O(1) token lookups.
    """
    def __init__(self, index_path='index.json', urls_path='urls.json', 
                 positions_path='token_positions.json', cache_size=100):
        """
        Initialize the index reader component.
        
        Args:
            index_path: Path to the inverted index JSON file
            urls_path: Path to the URLs mapping JSON file
            positions_path: Path to the token positions file
            cache_size: Number of terms to cache in memory
        """
        self.index_path = index_path
        
        # Initialize term cache
        self.cache = LRUCache(cache_size)
        
        # Load URL mappings - typically much smaller than the index
        with open(urls_path, 'r') as f:
            url_dict = json.load(f)
            # Convert string keys to integers
            self.urls = {int(k): v for k, v in url_dict.items()}
            
        # Load token positions for O(1) lookup
        try:
            with open(positions_path, 'r') as f:
                self.token_positions = json.load(f)
            print(f"Loaded {len(self.token_positions)} token positions for fast lookups")
        except FileNotFoundError:
            print(f"Warning: Token positions file {positions_path} not found. Lookups will be slower.")
            self.token_positions = {}
        
        # Total number of documents in the collection
        self.total_documents = len(self.urls)
    
    def get_postings_for_term(self, term):
        """
        Retrieve postings for a specific term from disk or cache using O(1) lookup.
        
        Args:
            term: The term to look up
            
        Returns:
            List of postings for the term, or empty list if term not found
        """
        # First check the cache
        cached_postings = self.cache.get(term)
        if cached_postings is not None:
            return cached_postings
            
        # If we have the position of this token in the index file
        if term in self.token_positions:
            try:
                with open(self.index_path, 'r') as f:
                    # Jump directly to the token's position
                    position = self.token_positions[term]
                    f.seek(position)
                    
                    # At this position, we should have: "token":[postings]
                    # First, read the token part
                    token_part = ""
                    # Read until we find the colon that separates token from postings
                    while True:
                        char = f.read(1)
                        if not char or char == ':':
                            break
                        token_part += char
                    
                    if not char or char != ':':
                        raise ValueError(f"Unexpected end of file or format when reading token '{term}'")
                    
                    # Now read opening bracket for the postings array
                    char = f.read(1)
                    if char != '[':
                        raise ValueError(f"Expected '[' for postings array, got '{char}'")
                    
                    # Now read the entire postings array
                    postings_str = '['  # Include the opening bracket
                    bracket_count = 1   # We've already read one opening bracket
                    
                    while bracket_count > 0:
                        char = f.read(1)
                        if not char:  # End of file
                            raise ValueError("Unexpected end of file while reading postings array")
                            
                        postings_str += char
                        
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                    
                    # Now postings_str should contain the complete JSON array
                    # But let's make sure it's valid by parsing it
                    try:
                        postings = json.loads(postings_str)
                        self.cache.put(term, postings)
                        return postings
                    except json.JSONDecodeError:
                        raise ValueError(f"Failed to parse postings array: {postings_str[:100]}...")
                        
            except (IOError, ValueError, json.JSONDecodeError) as e:
                print(f"Error reading postings for term '{term}': {e}")
                return []
        else:
            # If token isn't in our position dictionary, it doesn't exist in the index
            print(f"Token '{term}' not found in the index.")
            return []
    
    def has_term(self, term):
        """
        Check if a term exists in the index using O(1) lookup.
        
        Args:
            term: The term to check
            
        Returns:
            Boolean indicating if the term exists in the index
        """
        # First check the cache
        if self.cache.get(term) is not None:
            return True
            
        # Check if the term is in our positions dictionary
        return term in self.token_positions
            
    def get_document_frequency(self, term):
        """
        Get the document frequency for a term (number of documents containing the term).
        
        Args:
            term: The term to look up
            
        Returns:
            Document frequency of the term
        """
        postings = self.get_postings_for_term(term)
        return len(postings)

    def get_url(self, doc_id):
        """
        Get the URL for a document ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            URL string for the document
        """
        return self.urls.get(doc_id, None)
