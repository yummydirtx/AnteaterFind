class Posting:
    """
    A class representing a posting in an inverted index.
    Stores document ID and term frequency.
    """
    def __init__(self, doc_id: int, tf: float):
        """
        Initialize a posting with document ID and term frequency.
        Args:
            doc_id: ID of the document
            tf: Term frequency in the document
        """
        self.doc_id = doc_id  # Changed from doc_name to doc_id
        self.tf = tf

    def __lt__(self, other):
        """
        Less than comparison based on document ID.
        Args:
            other: Another posting instance
        Returns:
            bool: True if this posting's doc_id is less than the other's doc_id
        """
        return self.doc_id < other.doc_id

    def __str__(self) -> str:
        """
        Returns a string representation of the posting.
        Format: (document_id, tf)
        """
        return f"({self.doc_id}, {self.tf:.2f})"

    def to_dict(self):
        """
        Converts posting to dictionary format for JSON serialization.
        Returns:
            dict: Dictionary containing posting data
        """
        return {
            'doc_id': self.doc_id,
            'tf': self.tf
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
        return cls(data['doc_id'], data['tf'])
