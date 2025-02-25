from file import FileOpener
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, XMLParsedAsHTMLWarning
import warnings
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, RegexpTokenizer
from collections import Counter
import math
import json
import ijson

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    """
    Creates and manages an inverted index from a collection of documents.
    Implements disk-based indexing for memory efficiency.
    """
    def __init__(self, zipPath: str = None):
        """
        Initialize the inverted index. If zipPath is provided, immediately
        processes the documents in that path.
        """
        self.total_documents = 0
        self.stemmer = PorterStemmer()
        self.partial_index_count = 0
        if zipPath is not None:
            self.load_zip(zipPath)

    def load_zip(self, zipPath: str):
        """
        Processes documents from a ZIP file in batches to manage memory usage.
        Creates partial indexes for each batch.
        """
        file_opener = FileOpener(zipPath)
        try:
            while True:
                self.documents = file_opener.read_zip(15000)
                if not self.documents:
                    break
                batch_tfs = self.tokenize_documents()
                file_opener.save_partial_index(batch_tfs, self.partial_index_count)
                self.partial_index_count += 1
        finally:
            file_opener.close()
            if self.partial_index_count > 0:
                file_opener.merge_partial_indexes(self.partial_index_count)
                self.build_tfidf_index()

    def tokenize(self, text: str) -> dict:
        """
        Tokenizes HTML text using NLTK's word_tokenize and returns
        the frequency of each stemmed word.
        """
        # Parse HTML and extract text
        soup = BeautifulSoup(text, features='lxml')
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
        text = soup.get_text()

        # Create tokenizer that only captures alphanumeric
        tokenizer = RegexpTokenizer(r'[A-Za-z0-9]+')
        
        # Tokenize
        tokens = tokenizer.tokenize(text)
        
        # Stem tokens
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
        
        return dict(Counter(stemmed_tokens))

    def tokenize_documents(self) -> dict:
        """
        Tokenizes all documents in the ZIP file.
        """
        res = {}
        for doc_name, doc_text in self.documents.items():
            self.total_documents += 1
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

    def build_tfidf_index(self):
        with open("index.json", "rb") as f_in, open("tfidf.json", "w") as f_out:
            f_out.write("{")
            first_token = True
            parser = ijson.kvitems(f_in, "")
            for token, postings in parser:
                df = len(postings)
                idf = math.log10(self.total_documents / df)
                for p in postings:
                    p["tfidf"] = p["tf"] * idf
                    # Remove the term frequency
                    del p["tf"]
                if not first_token:
                    f_out.write(",")
                else:
                    first_token = False
                f_out.write(json.dumps(token))
                f_out.write(":")
                f_out.write(json.dumps(postings))
            f_out.write("}")
