from .file import FileOpener
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
            self.file_opener = FileOpener(zipPath)
            self.load_zip(zipPath)

    def load_zip(self, zipPath: str):
        """
        Processes documents from a ZIP file in batches to manage memory usage.
        Creates partial indexes for each batch.
        """
        try:
            while True:
                self.documents = self.file_opener.read_zip(15000)
                if not self.documents:
                    break
                batch_tfs = self.tokenize_documents()
                self.file_opener.save_partial_index(batch_tfs, self.partial_index_count)
                self.partial_index_count += 1
        finally:
            self.file_opener.close()
            if self.partial_index_count > 0:
                self.file_opener.merge_partial_indexes(self.partial_index_count)
    def weighted_tags(self, soup):
        """Gets text from within tags and applies weight"""
        tag_weights = {'h1': 4, 'h2': 3, 'h3': 2, 'b': 1.5, 'strong': 1.5} # b and strong are the same
        weighted_tokens = []
        #https://pytutorial.com/beautifulsoup-how-to-get-text-inside-tag-or-tgs/
        for tag, weight in tag_weights.items():
            for word in soup.find_all(tag):
                text = word.get_text()
                tokens = re.findall(r'\b[A-Za-z0-9]+\b', text)
                weighted_tokens.extend([token for token in tokens for _ in range(int(weight))])
        return weighted_tokens

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

        #weighted token
        weighted_tokens = self.weighted_tags(soup)

        # Stem tokens
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]

        all_tokens = weighted_tokens + stemmed_tokens
        
        return dict(Counter(all_tokens))

    def tokenize_documents(self) -> dict:
        """
        Tokenizes all documents in the ZIP file and calculates proper term frequencies.
        Returns a dictionary mapping document names to their term frequencies.
        """
        res = {}
        for doc_name, doc_text in self.documents.items():
            self.total_documents += 1
            # Get raw token counts
            token_counts = self.tokenize(doc_text)
            # Calculate normalized term frequencies
            res[doc_name] = self.calculate_tfs(token_counts)
        return res

    def calculate_tfs(self, tokens: dict) -> dict:
        """
        Calculates the term frequency of all tokens in a document.
        TF = number of times the token appears in the document / total number
        of tokens in the document.
        """
        total_tokens = sum(tokens.values())
        return {token: count / total_tokens for token, count in tokens.items()}


    def unique_tokens(self):
        """
        Count the unique tokens in the index.
        """
        try:
            # First try to use token positions file for a quick count
            with open('token_positions.json', 'r') as f:
                token_positions = json.load(f)
                return len(token_positions)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fall back to counting from the index file
            with open('index.json', 'r') as f:
                parser = ijson.kvitems(f, "")
                count = 0
                for _ in parser:
                    count += 1
            return count
