class Posting:
    def __init__(self,doc_name: str, tf: float, idf: float = None):
        """ intialize posting"""
        self.doc_name = doc_name
        self.tf = tf
        self.idf = idf
        self.tf_idf = tf * idf

    def __str__(self) -> str:
        """format for postings"""
        return f"({self.doc_name}, {self.tf_idf:.2f})"

    def to_dict(self):
        """Convert posting to dictionary for JSON serialization"""
        return {
            'doc_name': self.doc_name,
            'tf': self.tf
            #'idf': self.idf,
            #'tf_idf': self.tf_idf
        }

    @classmethod
    def from_dict(cls, data):
        """Create posting from dictionary"""
        posting = cls(data['doc_name'], data['tf'], 0)
        #posting.tf_idf = data['tf_idf']
        return posting
