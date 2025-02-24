class Posting:
    """
    A class representing a posting in an inverted index.
    Stores document name, term frequency, and optionally IDF and TF-IDF scores.
    """
    def __init__(self,doc_name: str, tf: float, idf: float = None):
        """
        Initialize a posting with document name and term frequency.
        Args:
            doc_name: Name of the document
            tf: Term frequency in the document
            idf: Optional inverse document frequency
        """
        self.doc_name = doc_name
        self.tf = tf
        if idf is not None:
            self.idf = idf
            self.tf_idf = tf * idf

    def __str__(self) -> str:
        """
        Returns a string representation of the posting.
        Format: (document_name, tf_idf_score)
        """
        return f"({self.doc_name}, {self.tf_idf:.2f})"

    def to_dict(self):
        """
        Converts posting to dictionary format for JSON serialization.
        Returns:
            dict: Dictionary containing posting data
        """
        return {
            'doc_name': self.doc_name,
            'tf': self.tf
            #'idf': self.idf,
            #'tf_idf': self.tf_idf
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Posting instance from a dictionary.
        Args:
            data: Dictionary containing posting data
        Returns:
            Posting: New posting instance
        """
        posting = cls(data['doc_name'], data['tf'], 0)
        #posting.tf_idf = data['tf_idf']
        return posting
