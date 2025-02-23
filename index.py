from file import FileOpener
from bs4 import BeautifulSoup
import json
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
        # Erase index.json
        with open('index.json', 'w') as f:
            f.write('')
        while True:
            self.documents = file_opener.read_zip(500)
            if len(self.documents) == 0:
                break
            batch_tokens = self.tokenize_documents()
            batch_tfs = {}
            for doc_name in batch_tokens:
                batch_tfs[doc_name] = self.calculate_tfs(batch_tokens[doc_name])
            # Write batch to index.json
            file_opener.write_batch_to_index(batch_tfs)

    def tokenize(self, text: str) -> dict:
        """
        Tokenizes HTML text into alphanumeric words using BeautifulSoup and returns 
        the frequency of each stemmed word.
        """
        # Parse HTML and extract text
        stemmer = PorterStemmer()
        soup = BeautifulSoup(text, features='xml')
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

    def get_unique_tokens(self):
        """Get set of unique tokens"""
        document_tokens = self.tokenize_documents()
        unique_tokens = set()
        for token in document_tokens.values():
            unique_tokens.update(token.keys())

        return unique_tokens
