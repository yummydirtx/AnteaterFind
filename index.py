from file import FileOpener
from bs4 import BeautifulSoup
import math
import re
from nltk.stem import PorterStemmer
from collections import Counter

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    def __init__(self, zipPath: str=None):
        if zipPath is not None:
            self.load_zip(zipPath)

    def load_zip(self, zipPath: str):
        file_opener = FileOpener(zipPath)
        self.documents = file_opener.read_zip()
        #create dict to map {token: list of postings} - posting might be {doc:tf-idf?}
        self.postings = self.calculate_tf_idfs()

    def tokenize(self, text: str) -> dict:
        """
        Tokenizes HTML text into alphanumeric words using BeautifulSoup and returns 
        the frequency of each stemmed word.
        """
        # Parse HTML and extract text
        stemmer = PorterStemmer()
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()

        # Find all alphanumeric sequences
        raw_tokens = re.findall(r'[A-Za-z0-9]+', text)

        # Convert all tokens to lowercase and stem them
        tokens = [stemmer.stem(token.lower()) for token in raw_tokens]

        return dict(Counter(tokens))
    
    def tokenize_documents(self) -> dict:
        """
        Tokenizes all documents in the ZIP file.
        """
        res = {}
        for doc_name, doc_text in self.documents.items():
            res[doc_name] = self.tokenize(doc_text)
        return res
    
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
            token_doc_counts[token] = math.log(total_docs / docs_with_token, 10) if docs_with_token > 0 else 0.0
        
        return token_doc_counts
    
    def calculate_tf_idfs(self) -> dict:
        """
        Calculates the TF-IDF of all tokens in all documents.
        """
        document_tokens = self.tokenize_documents()
        idfs = self.calculate_idfs(document_tokens)
        res = {}
        for doc_name, doc_tokens in document_tokens.items():
            tfs = self.calculate_tfs(doc_tokens)
            res[doc_name] = {token: tfs[token] * idfs[token] for token in doc_tokens}
        return res
