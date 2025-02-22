from file import FileOpener
import math
import re

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    def __init__(self, zipPath: str):
        file_opener = FileOpener(zipPath)
        self.documents = file_opener.read_zip()
        self.dict = {}
        #create dict to map {token: posting} - posting might be {doc:tf-idf?}

    def tokenize(self, text: str) -> dict:
        """
        Tokenizes text into alphanumeric words and returns the frequency of each word.
        """
        tokens = re.findall(r'\b[A-Za-z0-9]+\b', text)
        return {token: tokens.count(token) for token in tokens}

