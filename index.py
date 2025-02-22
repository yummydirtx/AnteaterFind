from file import FileOpener
import math
import re

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    def __init__(self, zipPath: str):
        file_opener = FileOpener(zipPath)
        self.documents = file_opener.read_zip()
        self.dict = {}
        #create dict to map {token: list of postings} - posting might be {doc:tf-idf?}

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
