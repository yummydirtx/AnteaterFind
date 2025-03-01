import math

class Ranking:
    def __init__(self, total_documents, search):
        self.total_documents = total_documents
        self.search = search

    def calculate_query_vector(self, query_terms):
        """
        Calculate the TF-IDF vector for the query.

        Args:
            query_terms: List of processed (stemmed) query terms

        Returns:
            Dictionary mapping terms to their TF-IDF values in the query
        """
        # Calculate term frequencies in the query
        query_tf = {}
        term_count = len(query_terms)

        for term in query_terms:
            query_tf[term] = query_tf.get(term, 0) + 1 / term_count

        # Calculate TF-IDF for each query term
        query_vector = {}
        for term, tf in query_tf.items():
            df = self.search.get_document_frequency(term)
            if df > 0:
                # IDF = log(total_documents / document_frequency)
                idf = math.log10(self.total_documents / df)
                query_vector[term] = tf * idf
            else:
                query_vector[term] = 0

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
            postings = self.search.get_postings_for_term(term)

            # Calculate IDF for this term
            df = len(postings)
            if df > 0:
                idf = math.log10(self.total_documents / df)
            else:
                idf = 0

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