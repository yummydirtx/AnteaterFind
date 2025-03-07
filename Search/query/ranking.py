import math

class Ranking:
    """
    The Ranking class provides functionality for scoring and ranking search results.
    
    This class works with the IndexReader to retrieve document information and
    compute similarity scores between queries and documents.
    """
    def __init__(self, total_documents, index_reader):
        self.total_documents = total_documents
        self.index_reader = index_reader
        self.idf_dict = {}

    def rank_results(self, results, query_terms):
        # Calculate query vector
        query_vector = self.ranking.calculate_query_vector(query_terms)
        
        # Calculate document vectors
        doc_vectors = self.ranking.calculate_document_vectors(results, query_terms)
        
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
        return results

    def get_idf(self, term):
        """Calculate idf once"""
        if term not in self.idf_dict:
            df = self.index_reader.get_document_frequency(term)
            if df == 0:
                return 0
            self.idf_dict[term] = math.log10((self.total_documents+1) / (df +1))
        return self.idf_dict[term]

    def calculate_query_vector(self, query_terms):
        """
        Calculate the TF-IDF vector for the query.

        Args:
            query_terms: List of processed (stemmed) query terms

        Returns:
            Dictionary mapping terms to their TF-IDF values in the query
        """
        #error handling
        if not query_terms:
            raise ValueError("Query cannot be empty")
        # Calculate term frequencies in the query
        query_tf = {}
        term_count = len(query_terms)

        for term in query_terms:
            query_tf[term] = query_tf.get(term, 0) + 1

        # Calculate TF-IDF for each query term
        query_vector = {}
        for term, tf in query_tf.items():
            idf = self.get_idf(term)
            query_vector[term] = tf * idf
        return query_vector

    def calculate_document_vectors(self, doc_ids, query_terms):
        """
        Calculate document vectors (limited to query terms) for the given document IDs.

        Args:
            doc_ids: Set of document IDs
            query_terms: List of processed query terms

        Returns:
            Dictionary mapping document IDs to their partial TF-IDF vectors
        """
        doc_vectors = {doc_id: {} for doc_id in doc_ids}

        for term in query_terms:
            idf = self.get_idf(term)
            postings = self.index_reader.get_postings_for_term(term)
            for posting in postings:
                doc_id = posting['doc_id']
                if doc_id in doc_ids:
                    # Store TF-IDF instead of just TF
                    doc_vectors[doc_id][term] = posting['tf'] * idf

        return doc_vectors

    def cosine_similarity(self, query_vector, doc_vector):
        """
        Calculate cosine similarity between query and document vectors.

        Args:
            query_vector: Dictionary mapping terms to TF-IDF values in the query
            doc_vector: Dictionary mapping terms to TF-IDF values in the document

        Returns:
            Cosine similarity score
        """
        # Find common terms
        common_terms = set(query_vector.keys()) & set(doc_vector.keys())

        if not common_terms:
            return 0.0

        # Calculate dot product
        dot_product = sum(query_vector[term] * doc_vector[term] for term in common_terms)

        # Calculate magnitudes
        query_magnitude = math.sqrt(sum(value ** 2 for value in query_vector.values()))
        doc_magnitude = math.sqrt(sum(value ** 2 for value in doc_vector.values()))

        if query_magnitude == 0 or doc_magnitude == 0:
            return 0.0

        return dot_product / (query_magnitude * doc_magnitude)
