from file import FileOpener
import math

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    def __init__(self):
        self.dict = {}
        #create dict to map {token: posting} - posting might be {doc:tf-idf?}

    def tokenize(self, text):
        #we use built in tokenize or one our groups
        pass