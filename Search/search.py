import json
from ranking import Ranking
import time
from cache import LRUCache
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from flask import Response

class Search:
    """
    Search component that handles retrieval of documents based on queries.
    Uses a disk-based approach with O(1) token lookups.
    """
    def __init__(self, index_path='index.json', urls_path='urls.json', 
                 positions_path='token_positions.json', cache_size=100):
        """
        Initialize the search component without loading the entire index.
        
        Args:
            index_path: Path to the inverted index JSON file
            urls_path: Path to the URLs mapping JSON file
            positions_path: Path to the token positions file
            cache_size: Number of terms to cache in memory
        """
        self.stemmer = PorterStemmer()
        self.tokenizer = RegexpTokenizer(r'[A-Za-z0-9]+')
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

        self.ranking = Ranking(self.total_documents, self)
        
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

    def tokenize_query(self, query):
        """
        Tokenize and stem query text using the same process as document indexing.
        
        Args:
            query: The search query string
            
        Returns:
            List of stemmed query terms
        """
        # Tokenize
        tokens = self.tokenizer.tokenize(query.lower())
        
        # Stem tokens
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
        
        return stemmed_tokens

    def boolean_and_search(self, query_terms):
        """
        Perform a boolean AND search using the provided query terms.
        
        Args:
            query_terms: List of processed (stemmed) query terms
            
        Returns:
            Set of document IDs that contain all query terms
        """
        if not query_terms:
            return set()
            
        # Find the least frequent term first to minimize initial result set
        term_frequencies = [(term, self.get_document_frequency(term)) for term in query_terms]
        term_frequencies.sort(key=lambda x: x[1])  # Sort by frequency (ascending)
        
        # If any term doesn't exist in the index, return empty set
        if any(freq == 0 for _, freq in term_frequencies):
            return set()
            
        # Start with documents containing the least frequent term
        first_term = term_frequencies[0][0]
        postings = self.get_postings_for_term(first_term)
        result_docs = set(posting['doc_id'] for posting in postings)
        
        # Intersect with documents containing each subsequent term
        for term, _ in term_frequencies[1:]:
            term_postings = self.get_postings_for_term(term)
            term_docs = set(posting['doc_id'] for posting in term_postings)
            result_docs &= term_docs
            
            # Early termination if intersection becomes empty
            if not result_docs:
                break
                
        return result_docs

    def search(self, query, use_ranking=True):
        """
        Search for documents matching the query.
        
        Args:
            query: The search query string
            use_ranking: Whether to rank results by relevance (default: True)
            
        Returns:
            List of (doc_id, url, composite_score, tf_idf_info) tuples for matching documents
        """
        # Process query
        query_terms = self.tokenize_query(query)
        
        if not query_terms:
            return []
        
        # Get matching documents using boolean AND
        matching_doc_ids = self.boolean_and_search(query_terms)
        
        if not matching_doc_ids:
            return []
            
        results = []
        
        if use_ranking:
            # Calculate query vector
            query_vector = self.ranking.calculate_query_vector(query_terms)
            
            # Calculate document vectors
            doc_vectors = self.ranking.calculate_document_vectors(matching_doc_ids, query_terms)
            
            # Calculate scores using both metrics
            scores = []
            
            for doc_id, doc_vector in doc_vectors.items():
                # Calculate cosine similarity (primary sort criteria)
                cosine_sim = self.ranking.cosine_similarity(query_vector, doc_vector)
                
                # Calculate TF-IDF average (secondary sort criteria)
                tf_idf_avg = sum(doc_vector.values()) / len(query_terms)
                
                # Store both metrics for sorting
                scores.append((doc_id, cosine_sim, tf_idf_avg, doc_vector))
            
            # Sort first by cosine similarity, then by TF-IDF average
            scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
            
            # Create a composite score that combines both metrics for display
            # Use cosine similarity as the main score, but keep it separate internally
            results = [(doc_id, self.urls[doc_id], cosine_sim, doc_vector) 
                      for doc_id, cosine_sim, _, doc_vector in scores]
        else:
            # Just return matching documents without scoring
            results = [(doc_id, self.urls[doc_id], 1.0, {}) for doc_id in matching_doc_ids]
            
        return results
    
    def get_formatted_results(self, query, jsonify, limit=5) -> Response:
        """
        Get search results in a formatted manner for display.
        
        Args:
            query: The search query string
            limit: Maximum number of results to display (default: 5)
        """
        start_time = time.time()
        results = self.search(query)
        query_time = time.time() - start_time
        formatted_results = [ {
            "doc_id": doc_id,
            "url": url,
            "score": score,
            "tf_idf_info": tf_idf_info
        } for doc_id, url, score, tf_idf_info in results[:limit]
        ]
        return jsonify({"results": formatted_results, "total": len(results), "query_time": query_time})

    def print_results(self, results, limit=10):
        """
        Print search results in a formatted manner, including TF-IDF values.
        
        Args:
            results: List of (doc_id, url, score, tf_idf_info) tuples
            limit: Maximum number of results to display (default: 10)
        """
        print(f"Found {len(results)} matching documents.")
        
        for i, (doc_id, url, score, tf_idf_info) in enumerate(results[:limit]):
            print(f"{i+1}. [Score: {score:.4f}] Document {doc_id}: {url}")
            
            # Display TF-IDF information for the terms
            if tf_idf_info:
                print("  TF-IDF values:")
                # Sort terms by TF-IDF value for better readability
                sorted_terms = sorted(tf_idf_info.items(), key=lambda x: x[1], reverse=True)
                for term, tf_idf in sorted_terms:
                    print(f"    - {term}: {tf_idf:.4f}")
            
        if len(results) > limit:
            print(f"... and {len(results) - limit} more results.")
