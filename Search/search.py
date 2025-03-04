import time
from flask import Response
from .summarizer import summarize
from .query import Ranking, QueryProcessor
from .indexing import IndexReader

class Search:
    """
    Search component that handles retrieval of documents based on queries.
    Uses a disk-based approach with O(1) token lookups.
    """
    def __init__(self, zip_path='zips/developer.zip', index_path='index.json', urls_path='urls.json', 
                 positions_path='token_positions.json', cache_size=100):
        """
        Initialize the search component without loading the entire index.
        
        Args:
            index_path: Path to the inverted index JSON file
            urls_path: Path to the URLs mapping JSON file
            positions_path: Path to the token positions file
            cache_size: Number of terms to cache in memory
        """
        # Initialize components
        self.index_reader = IndexReader(zip_path, index_path, urls_path, positions_path, cache_size)
        self.query_processor = QueryProcessor(self.index_reader)
        self.ranking = Ranking(self.index_reader.total_documents, self.index_reader)

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
        query_terms = self.query_processor.tokenize_query(query)
        
        if not query_terms:
            return []
        
        # Get matching documents using boolean AND
        matching_doc_ids = self.query_processor.boolean_and_search(query_terms)
        
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
            results = [(doc_id, self.index_reader.get_url(doc_id), cosine_sim, doc_vector) 
                      for doc_id, cosine_sim, _, doc_vector in scores]
        else:
            # Just return matching documents without scoring
            results = [(doc_id, self.index_reader.get_url(doc_id), 1.0, {}) for doc_id in matching_doc_ids]
            
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

    def get_summary(self, site_id, api_key, jsonify):
        """
        Get a summary of the indexed site using the OpenAI API.

        Args:
            site_id: The document ID of the site to summarize
            api_key: The OpenAI API key for authentication
            jsonify: Function to jsonify the response
        """
        file_content = self.index_reader.get_document_contents(site_id)
        summary = summarize(file_content, api_key)
        if summary:
            return jsonify({"summary": summary})
        else:
            return jsonify({"error": "Failed to generate summary."})
