from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

class QueryProcessor:
    """
    Handles query processing, tokenization, and boolean operations.
    """
    def __init__(self, index_reader):
        """
        Initialize the query processor.
        
        Args:
            index_reader: IndexReader instance for retrieving document information
        """
        self.stemmer = PorterStemmer()
        self.tokenizer = RegexpTokenizer(r'[A-Za-z0-9]+')
        self.index_reader = index_reader

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
        term_frequencies = [(term, self.index_reader.get_document_frequency(term)) for term in query_terms]
        term_frequencies.sort(key=lambda x: x[1])  # Sort by frequency (ascending)
        
        # If any term doesn't exist in the index, return empty set
        if any(freq == 0 for _, freq in term_frequencies):
            return set()
            
        # Start with documents containing the least frequent term
        first_term = term_frequencies[0][0]
        postings = self.index_reader.get_postings_for_term(first_term)
        result_docs = set(posting['doc_id'] for posting in postings)
        
        # Intersect with documents containing each subsequent term
        for term, _ in term_frequencies[1:]:
            term_postings = self.index_reader.get_postings_for_term(term)
            term_docs = set(posting['doc_id'] for posting in term_postings)
            result_docs &= term_docs
            
            # Early termination if intersection becomes empty
            if not result_docs:
                break
                
        return result_docs
