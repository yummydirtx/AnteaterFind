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
        if zipPath is not None:
            self.load_zip(zipPath)
            self.merge_partial_indexes()

    def load_zip(self, zipPath: str):
        file_opener = FileOpener(zipPath)
        try:
            while True:
                documents = file_opener.read_zip(10000)
                if not documents:
                    break
                batch_tfs = {}
                for doc_name, doc_text in documents.items():
                    self.total_documents += 1
                    tokens = self.tokenize(doc_text)
                    batch_tfs[doc_name] = self.calculate_tfs(tokens)
                self.save_partial_index(batch_tfs)
        finally:
            file_opener.close()

    def save_partial_index(self, batch_tfs: dict):
        """Save a partial index to disk"""
        partial_index = defaultdict(list)
        for doc_name, tokens in batch_tfs.items():
            for token, tf in tokens.items():
                partial_index[token].append(Posting(doc_name, tf, 0))
        
        # Save partial index to disk
        self.partial_index_count += 1
        with open(f'partial_index_{self.partial_index_count}.json', 'w') as f:
            json.dump({k: [vars(p) for p in v] for k, v in partial_index.items()}, f)

    def merge_partial_indexes(self):
        """Merge all partial indexes using k-way merge"""
        
        # Open all partial index files
        files = [f'partial_index_{i}.json' for i in range(1, self.partial_index_count + 1)]
        file_iterators = []
        
        # Create iterators for each file
        for fname in files:
            with open(fname, 'r') as f:
                data = json.load(f)
                file_iterators.append(iter(sorted(data.items())))

        # Initialize heap with first item from each iterator
        heap = []
        for i, it in enumerate(file_iterators):
            try:
                token, postings = next(it)
                heap.append((token, i, postings))
            except StopIteration:
                pass
        heapq.heapify(heap)

        # Merge
        current_token = None
        current_postings = []
        
        with open('index.json', 'w') as outfile:
            outfile.write('{')
            first_token = True
            
            while heap:
                token, file_index, postings = heapq.heappop(heap)
                
                # Try to get next item from the same file
                try:
                    next_token, next_postings = next(file_iterators[file_index])
                    heapq.heappush(heap, (next_token, file_index, next_postings))
                except StopIteration:
                    pass

                if current_token != token:
                    # Write accumulated postings for previous token
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

            # Write last token
            if current_token is not None:
                if not first_token:
                    outfile.write(',')
                json.dump(current_token, outfile)
                outfile.write(':')
                json.dump(current_postings, outfile)
            
            outfile.write('}')

        # Clean up partial index files
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

    def update_index(self, batch_tfs: dict):
        for doc_name, tokens in batch_tfs.items():
            for token, tf in tokens.items():
                self.index[token].append(Posting(doc_name, tf, 0))

    def get_unique_tokens(self):
        """Get set of unique tokens"""
        tokens = set()
        with open('index.json', 'r') as f:
            # Read file in chunks to avoid loading entire file
            chunk_size = 1024 * 1024  # 1MB chunks
            chunk = f.read(chunk_size)
            current_token = ''
            in_string = False
            
            while chunk:
                for char in chunk:
                    if char == '"' and (len(current_token) == 0 or current_token[-1] != '\\'):
                        in_string = not in_string
                        if not in_string and current_token:
                            tokens.add(current_token)
                            current_token = ''
                    elif in_string:
                        current_token += char
                chunk = f.read(chunk_size)
                
        return tokens