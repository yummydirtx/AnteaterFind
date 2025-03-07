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
        
        # Batch retrieve all term frequencies in one go
        # (assuming index_reader supports batch operations, or implement if needed)
        term_frequencies = self.index_reader.get_document_frequencies(query_terms)
        
        # Filter out terms that don't exist in the index
        valid_terms = [(term, freq) for term, freq in term_frequencies.items() if freq > 0]
        
        if not valid_terms:
            return set()
        
        # Sort by frequency for optimal processing
        valid_terms.sort(key=lambda x: x[1])
        
        # Batch retrieve postings for all terms
        terms = [term for term, _ in valid_terms]
        all_postings = self.index_reader.get_postings_for_terms(terms)
        
        # Start with the smallest set
        first_term = valid_terms[0][0]
        result_docs = set(posting['doc_id'] for posting in all_postings[first_term])
        
        # Intersect with remaining terms
        for term, _ in valid_terms[1:]:
            term_docs = set(posting['doc_id'] for posting in all_postings[term])
            result_docs &= term_docs
            
            # Early termination if intersection becomes empty
            if not result_docs:
                break
                
        return result_docs
