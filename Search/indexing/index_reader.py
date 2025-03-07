import json
from bs4 import BeautifulSoup
import zipfile
from .cache import LRUCache

class IndexReader:
    """
    Handles disk-based index reading operations with O(1) token lookups.
    """
    def __init__(self, zip_path='zips/developer.zip', index_path='index.json', urls_path='urls.json', 
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
        self.zip_path = zip_path
        
        # Initialize term cache
        self.cache = LRUCache(cache_size)
        
        # Load URL mappings - typically much smaller than the index
        with open(urls_path, 'r') as f:
            url_dict = json.load(f)
            # Convert string keys to integers
            self.urls = {int(k): v for k, v in url_dict.items()}

        # Load file mappings
        with open('files.json', 'r') as f:
            file_dict = json.load(f)
            # Convert string keys to integers
            self.files = {int(k): v for k, v in file_dict.items()}
            
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
    
    def get_postings_for_terms(self, terms):
        """
        Retrieve postings for a list of terms efficiently with minimal disk I/O.
        
        Args:
            terms: List of terms to retrieve postings for
            
        Returns:
            Dictionary mapping terms to their postings lists
        """
        # Initialize results dictionary
        result = {}
        
        # Check which terms are already in cache
        terms_to_fetch = []
        for term in terms:
            cached_postings = self.cache.get(term)
            if cached_postings is not None:
                result[term] = cached_postings
            elif term in self.token_positions:  # Only add terms that exist in the index
                terms_to_fetch.append(term)
            else:
                result[term] = []  # Term not in index
        
        if not terms_to_fetch:
            return result
        
        # Sort terms by their position in the file to minimize seeking
        terms_to_fetch.sort(key=lambda t: self.token_positions[t])
        
        try:
            with open(self.index_path, 'r') as f:
                for term in terms_to_fetch:
                    position = self.token_positions[term]
                    f.seek(position)
                    
                    # Read until we find the colon that separates token from postings
                    token_part = ""
                    while True:
                        char = f.read(1)
                        if not char or char == ':':
                            break
                        token_part += char
                    
                    if not char or char != ':':
                        continue  # Skip if unexpected format
                    
                    # Read opening bracket for the postings array
                    char = f.read(1)
                    if char != '[':
                        continue  # Skip if unexpected format
                    
                    # Read the entire postings array
                    postings_str = '['
                    bracket_count = 1
                    
                    while bracket_count > 0:
                        char = f.read(1)
                        if not char:  # End of file
                            break
                            
                        postings_str += char
                        
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                    
                    try:
                        postings = json.loads(postings_str)
                        self.cache.put(term, postings)
                        result[term] = postings
                    except json.JSONDecodeError:
                        result[term] = []  # Use empty list on error
                        
        except IOError as e:
            print(f"Error reading postings: {e}")
            # For any terms we couldn't read, set empty postings
            for term in terms_to_fetch:
                if term not in result:
                    result[term] = []
        
        return result
    
    def get_postings_for_term(self, term):
        """
        Retrieve postings for a single term using the batch method.
        
        Args:
            term: The term to look up
            
        Returns:
            List of postings for the term, or empty list if term not found
        """
        return self.get_postings_for_terms([term]).get(term, [])
    
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
    
    def get_document_frequencies(self, query_terms):
        """
        Get the document frequencies for a list of query terms.
        
        Args:
            query_terms: List of query terms (may contain duplicates)
        Returns:
            Dictionary mapping terms to their document frequencies
        """
        # Convert to set to remove duplicates before processing
        unique_terms = set(query_terms)
        postings_dict = self.get_postings_for_terms(list(unique_terms))
        return {term: len(postings) for term, postings in postings_dict.items()}

    def get_url(self, doc_id):
        """
        Get the URL for a document ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            URL string for the document
        """
        return self.urls.get(doc_id, None)
    
    def get_document_contents(self, doc_id):
        """
        Get the contents of a document by its ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document contents as a string
        """
        file_name = self.files.get(int(doc_id))
        if file_name is None:
            return None
        with zipfile.ZipFile(self.zip_path) as z:
            with z.open(file_name) as f:
                for line in f:
                    try:
                        json_data = json.loads(line.decode('utf-8'))
                        if 'content' in json_data:
                            content = json_data['content']
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in file: {file_name}")
        soup = BeautifulSoup(content, features='lxml')
        return soup.get_text()
