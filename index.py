from file import FileOpener
import math
import re

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    def __init__(self, zipPath: str):
        file_opener = FileOpener(zipPath)
        self.documents = file_opener.read_zip()
        #create dict to map {token: list of postings} - posting might be {doc:tf-idf?}
        self.dict = self.calculate_tf_idfs()

    def tokenize(self, text: str) -> dict:
        """
        Tokenizes text into alphanumeric words and returns the frequency of each word.
        """
        tokens = re.findall(r'\b[A-Za-z0-9]+\b', text)
        return {token: tokens.count(token) for token in tokens}
    
    def calculate_tfs(self, tokens: dict) -> dict:
        """
        Calculates the term frequency of all tokens in a document.
        TF = number of times the token appears in the document / total number
        of tokens in the document.
        """
        total_tokens = sum(tokens.values())
        return {token: count / total_tokens for token, count in tokens.items()}
    
    def calculate_idfs(self, document_tokens: dict) -> dict:
        """
        Calculates the inverse document frequency of all tokens.
        IDF = log(total number of documents / number of documents containing the token)
        document_tokens = {doc_name: {token: count}}
        """ 
        total_docs = len(self.documents)
        token_doc_counts = {}
        # Count documents containing each token
        for token in set().union(*document_tokens.values()):
            # Count the number of documents containing the token
            docs_with_token = sum(1 for doc_tokens in document_tokens.values() 
                    if token in doc_tokens)
            # Calculate the IDF
            token_doc_counts[token] = math.log(total_docs / docs_with_token)
        
        return token_doc_counts
    
    def calculate_tf_idfs(self) -> dict:
        pass


