class Posting:
    def __init__(self,doc_name: str, tf: float, idf: float):
        """ intialize posting"""
        self.doc_name = doc_name
        self.tf = tf
        self.idf = idf
        self.tf_idf = tf * idf

    def __str__(self) -> str:
        "format for postings"
        return f"({self.doc_name}, {self.tf_idf})"