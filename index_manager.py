import json
import heapq
import math
import os
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import ijson
from tqdm import tqdm
from posting import Posting

class IndexManager:
    def __init__(self):
        self.url_to_id = {}  # Map URLs to numeric IDs
        self.current_url_id = 0

    def get_url_id(self, url: str) -> int:
        """Get or create a numeric ID for a URL"""
        if url not in self.url_to_id:
            self.url_to_id[url] = self.current_url_id
            self.current_url_id += 1
        return self.url_to_id[url]

    def save_url_mapping(self):
        """Save the URL to ID mapping to a separate file"""
        id_to_url = {str(id): url for url, id in self.url_to_id.items()}
        with open('urls.json', 'w') as f:
            json.dump(id_to_url, f)

    def create_partial_index(self, batch_tfs: Dict[str, Dict[str, int]]) -> Dict[str, List[Posting]]:
        """Creates a partial index from batch of tfs"""
        partial_index = defaultdict(list)
        for url, tokens in batch_tfs.items():
            url_id = self.get_url_id(url)
            for token, tf in tokens.items():
                partial_index[token].append(Posting(url_id, tf))
        return partial_index

    def write_partial_index(self, partial_index: Dict[str, List[Posting]], filename: str):
        """
        writes partial index to file in a sorted order
        Each partial index is sorted and contains one token entry per line.
        """
        with open(filename, 'w') as f:
            for token in sorted(partial_index.keys()):
                entry = {
                    "token": token,
                    "postings": [vars(p) for p in partial_index[token]]
                }
                f.write(json.dumps(entry) + "\n")
    
    def save_partial_index(self, batch_tfs: Dict[str, Dict[str, int]], partial_index_count: int):
        """saves partial index to disk"""
        partial_index = self.create_partial_index(batch_tfs)
        filename = f'partial_index_{partial_index_count}.json'
        self.write_partial_index(partial_index, filename)
        return filename

    def _initialize_file_iterators(self, files: List[str], merge_pbar):
        """Initialize file iterators for each partial index file"""
        file_iters = []
        for fname in files:
            fp = open(fname, 'r')
            line = fp.readline()
            if line:
                data = json.loads(line)
                file_iters.append((data["token"], data["postings"], fp))
            else:
                fp.close()
            merge_pbar.update(1)
        return file_iters

    def _initialize_heap(self, file_iters):
        """Initialize the heap with the first entry from each file"""
        heap = []
        counter = 0
        for token, postings, fp in file_iters:
            heap.append((token, counter, postings, fp))
            counter += 1
        heapq.heapify(heap)
        return heap, counter

    def _write_current_token(self, outfile, current_token, current_postings, first_token):
        """Write the current token and its postings to the output file"""
        if not first_token:
            outfile.write(',')
        json.dump(current_token, outfile)
        outfile.write(':')
        json.dump(current_postings, outfile)

    def merge_partial_indexes(self, partial_index_count: int):
        """Merge partial indexes using a k-way merge without loading everything into memory."""
        self.save_url_mapping()

        files = [f'partial_index_{i}.json' for i in range(0, partial_index_count)]
        merge_pbar = tqdm(total=partial_index_count, desc="Merging partial indexes")

        file_iters = self._initialize_file_iterators(files, merge_pbar)
        
        merge_pbar.reset()
        merge_pbar.set_description("Processing tokens")
        merge_pbar.total = None

        heap, counter = self._initialize_heap(file_iters)

        with open('index.json', 'w') as outfile:
            outfile.write('{')
            first_token = True
            current_token = None
            current_postings = []

            while heap:
                token, _, postings, fp = heapq.heappop(heap)
                
                if current_token is None or token != current_token:
                    if current_token is not None:
                        self._write_current_token(outfile, current_token, current_postings, first_token)
                        first_token = False
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
                self._write_current_token(outfile, current_token, current_postings, first_token)
            outfile.write('}')

        merge_pbar.close()

        # Clean up temporary files
        for fname in files:
            os.remove(fname)

    def write_tfidf_index(self, total_documents: int):
        """Calculate and write the TF-IDF index to disk"""
        pbar = tqdm(desc="Calculating TF-IDF")
        with open("index.json", "rb") as f_in, open("tfidf.json", "w") as f_out:
            f_out.write("{")
            first_token = True
            parser = ijson.kvitems(f_in, "")
            for token, postings in parser:
                pbar.update(1)
                df = len(postings)
                idf = math.log10(total_documents / df)
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
        pbar.close()
