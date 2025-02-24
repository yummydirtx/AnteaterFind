from file import FileOpener
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
import json
import re
from nltk.stem import PorterStemmer
from collections import Counter, defaultdict
from posting import Posting
import heapq
from itertools import islice
import os

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

class InvertedIndex:
    def __init__(self, zipPath: str = None):
        self.total_documents = 0
        self.stemmer = PorterStemmer()
        self.partial_index_count = 0
        self.unique_tokens = set()
        if zipPath is not None:
            self.load_zip(zipPath)
            self.merge_partial_indexes()

    def load_zip(self, zipPath: str):
        file_opener = FileOpener(zipPath)
        try:
            while True:
                self.documents = file_opener.read_zip(15000)
                if not self.documents:
                    break
                batch_tfs = self.tokenize_documents()
                self.save_partial_index(batch_tfs)
        finally:
            file_opener.close()

    def save_partial_index(self, batch_tfs: dict):
        """Save a partial index to disk as a sorted, line-delimited file."""
        partial_index = defaultdict(list)
        for doc_name, tokens in batch_tfs.items():
            for token, tf in tokens.items():
                partial_index[token].append(Posting(doc_name, tf))
        
        self.partial_index_count += 1
        filename = f'partial_index_{self.partial_index_count}.json'
        with open(filename, 'w') as f:
            # Write one token entry per line in sorted order
            for token in sorted(partial_index.keys()):
                entry = {
                    "token": token,
                    "postings": [vars(p) for p in partial_index[token]]
                }
                f.write(json.dumps(entry) + "\n")

    def merge_partial_indexes(self):
        """Merge partial indexes using a k-way merge without loading everything into memory."""
        files = [f'partial_index_{i}.json' for i in range(1, self.partial_index_count + 1)]
        
        file_iters = []
        for fname in files:
            fp = open(fname, 'r')
            line = fp.readline()
            if line:
                data = json.loads(line)
                file_iters.append((data["token"], data["postings"], fp))
            else:
                fp.close()
        
        # Add a counter as tie-breaker
        counter = 0
        heap = []
        for token, postings, fp in file_iters:
            heap.append((token, counter, postings, fp))
            counter += 1
        heapq.heapify(heap)

        with open('index.json', 'w') as outfile:
            outfile.write('{')
            first_token = True
            current_token = None
            current_postings = []
            
            while heap:
                token, _, postings, fp = heapq.heappop(heap)
                if current_token is None or token != current_token:
                    if current_token is not None:
                        if not first_token:
                            outfile.write(',')
                        else:
                            first_token = False
                        json.dump(current_token, outfile)
                        outfile.write(':')
                        json.dump(current_postings, outfile)
                    current_token = token
                    current_postings = postings
                else:
                    current_postings.extend(postings)
                
                next_line = fp.readline()
                if next_line:
                    data = json.loads(next_line)
                    heapq.heappush(heap, (data["token"], counter, data["postings"], fp))
                    counter += 1
                else:
                    fp.close()
            if current_token is not None:
                if not first_token:
                    outfile.write(',')
                json.dump(current_token, outfile)
                outfile.write(':')
                json.dump(current_postings, outfile)
            outfile.write('}')
        
        # Remove partial index files
        for fname in files:
            os.remove(fname)

    def tokenize(self, text: str) -> dict:
        """
        Tokenizes HTML text into alphanumeric words using BeautifulSoup and returns
        the frequency of each stemmed word.
        """
        # Parse HTML and extract text
        soup = BeautifulSoup(text, features='xml')
        warnings.filterwarnings("ignore", category = MarkupResemblesLocatorWarning)
        text = soup.get_text()

        # Find all alphanumeric sequences
        raw_tokens = re.findall(r'[A-Za-z0-9]+', text)

        # Convert all tokens to lowercase and stem them
        tokens = [self.stemmer.stem(token.lower()) for token in raw_tokens]

        # Add tokens to set of unique tokens
        self.unique_tokens.update(tokens)

        return dict(Counter(tokens))

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

    def get_unique_tokens(self):
        """Get number of unique tokens"""
        return len(self.unique_tokens)

if __name__ == "__main__":
    index = InvertedIndex()
    index.partial_index_count = 3
    index.merge_partial_indexes()
    print(f"Total documents indexed: {index.total_documents}")
    print(f"Unique tokens: {index.get_unique_tokens()}")