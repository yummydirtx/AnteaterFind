from .file import FileOpener
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, XMLParsedAsHTMLWarning
import warnings
import re
from nltk.stem import PorterStemmer
from collections import Counter
import json
import ijson
import multiprocessing
from functools import partial
import tqdm

# how to find the tf-idf https://www.learndatasci.com/glossary/tf-idf-term-frequency-inverse-document-frequency/

def weighted_tags(soup) -> list:
    """
    Process tokens if they have tags (ie: h1, h2, h3, b, strong)
    Args:
        soup: BeautifulSoup object

    Returns:
        List of tokens that are duplicated based on weights given
    """

    tag_weights = {'h1': 4, 'h2': 3, 'h3': 2, 'b': 1.5, 'strong': 1.5}
    weighted_tokens = []
    
    # Process all tags in one pass
    for tag in soup.find_all(list(tag_weights.keys())):
        weight = tag_weights.get(tag.name, 1)
        tokens = re.findall(r'\b[A-Za-z0-9]+\b', tag.get_text().lower())
        weighted_tokens.extend([token for token in tokens for _ in range(int(weight))])
    
    return weighted_tokens

# Worker function for multiprocessing
def tokenize_chunk(chunk, stemmer):
    """
    Process a chunk of documents in a separate process
    
    Args:
        chunk: Dictionary of document name to document text
        stemmer: PorterStemmer instance
        
    Returns:
        Dictionary mapping document names to their raw token counts
    """
    result = {}
    for doc_name, doc_text in chunk.items():
        # Parse HTML and extract text

        #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#specifying-the-parser-to-use should fix broken html files
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
        soup = BeautifulSoup(doc_text, features='lxml')
        text = soup.get_text(separator=" ")

        # Tokenize using regex
        tokens = re.findall(r'[A-Za-z0-9]+', text.lower())
        
        # Extract weighted tokens
        weighted_tokens = weighted_tags(soup)
        weighted_tokens = [stemmer.stem(token.lower()) for token in weighted_tags(soup)]

        # Stem tokens
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        
        all_tokens = weighted_tokens + stemmed_tokens
        
        # Just store raw token counts
        result[doc_name] = dict(Counter(all_tokens))
    
    return result

class InvertedIndex:
    """
    Creates and manages an inverted index from a collection of documents.
    Implements disk-based indexing for memory efficiency.
    """
    def __init__(self, zipPath: str = None, simhash_threshold: int = 5):
        """
        Initialize the inverted index. If zipPath is provided, immediately
        processes the documents in that path.
        """
        self.total_documents = 0
        self.stemmer = PorterStemmer()
        self.partial_index_count = 0
        if zipPath is not None:
            self.file_opener = FileOpener(zipPath, simhash_threshold)
            self.load_zip()

    def load_zip(self):
        """
        Processes documents from a ZIP file in batches to manage memory usage.
        Creates partial indexes for each batch.
        """
        try:
            while True:
                # Read batches so there are 3 partial indexes
                count = self.file_opener.total_files // 3
                self.documents = self.file_opener.read_zip(count)
                if not self.documents:
                    break
                batch_tfs = self.tokenize_documents()
                self.file_opener.save_partial_index(batch_tfs, self.partial_index_count)
                self.partial_index_count += 1
        finally:
            self.file_opener.close()
            if self.partial_index_count > 0:
                self.file_opener.merge_partial_indexes(self.partial_index_count)

    def tokenize_documents(self) -> dict:
        """
        Tokenizes all documents in the ZIP file and calculates proper term frequencies.
        Uses multiprocessing for faster processing by dividing documents into chunks.
        Returns:
            dict: a dictionary mapping document names to their term frequencies.
        """

        # Determine optimal number of processes
        num_processes = min(multiprocessing.cpu_count(), len(self.documents))
        
        # Split documents into chunks for parallel processing
        chunk_size = max(1, len(self.documents) // num_processes)
        chunks = [dict(list(self.documents.items())[i:i + chunk_size]) 
                 for i in range(0, len(self.documents), chunk_size)]
        
        # Process chunks in parallel to get raw token counts
        with multiprocessing.Pool(processes=num_processes) as pool:
            raw_results = list(tqdm.tqdm(
                pool.imap(partial(tokenize_chunk, stemmer=self.stemmer), chunks),
                total=len(chunks),
                desc="Tokenizing documents",
                unit="chunk",
                leave=False
            ))
        
        # Combine results from all processes
        token_counts = {}
        for chunk_result in raw_results:
            token_counts.update(chunk_result)
        
        # Now calculate term frequencies from the complete token counts
        term_frequencies = {}
        for doc_name, counts in token_counts.items():
            term_frequencies[doc_name] = self.calculate_tfs(counts)
        
        self.total_documents += len(self.documents)
        return term_frequencies

    def calculate_tfs(self, tokens: dict) -> dict:
        """
        Calculates the term frequency of all tokens in a document.
        TF = number of times the token appears in the document / total number
        of tokens in the document.
        Args:
            tokens (dict): Dictionary mapping of token and its raw frequencies
        Returns:
            dict: Dictionary mapping tokens to their normalized term frequencies.
        """
        total_tokens = sum(tokens.values())
        return {token: count / total_tokens for token, count in tokens.items()}


    def unique_tokens(self):
        """
        Count the unique tokens in the index.
        First tries token_position.json for quicker access
        if missing tries counting from index.json
        Returns:
            int: Number of unique tokens in the index
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
