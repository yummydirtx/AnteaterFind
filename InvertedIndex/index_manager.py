import json
import heapq
import os
import pickle
from collections import defaultdict
from typing import Dict, List
from tqdm import tqdm
from .posting import Posting

class IndexManager:
    def __init__(self):
        self.url_to_id = {}  # Map URLs to numeric IDs
        self.file_to_id = {}
        self.current_url_id = 0
        self.current_file_id = 0

    def get_url_id(self, url: str) -> int:
        """Get or create a numeric ID for a URL"""
        if url not in self.url_to_id:
            self.url_to_id[url] = self.current_url_id
            self.current_url_id += 1
        return self.url_to_id[url]
    
    def get_file_id(self, file_path: str) -> int:
        """Get or create a numeric ID for a file path"""
        if file_path not in self.file_to_id:
            self.file_to_id[file_path] = self.current_file_id
            self.current_file_id += 1
        return self.file_to_id[file_path]
    
    def save_file_mapping(self):
        """Save the file path to ID mapping to a separate file"""
        id_to_file = {str(id): file_path for file_path, id in self.file_to_id.items()}
        with open('files.json', 'w') as f:
            json.dump(id_to_file, f)

    def save_url_mapping(self):
        """Save the URL to ID mapping to a separate file"""
        id_to_url = {str(id): url for url, id in self.url_to_id.items()}
        with open('urls.json', 'w') as f:
            json.dump(id_to_url, f)

    def create_and_save_partial_index(self, batch_tfs: Dict[str, Dict[str, int]], partial_index_count: int) -> str:
        """
        Creates a partial index from batch of tfs and saves it to disk
        
        Args:
            batch_tfs: Dictionary mapping URLs to their token frequency dictionaries
            partial_index_count: Counter to identify this partial index
            
        Returns:
            filename: Name of the file where the partial index was saved
        """
        # Create partial index
        with tqdm(total=len(batch_tfs), desc="Creating partial index", leave=False) as pbar:
            partial_index = defaultdict(list)
            for (url, file_path), tokens in batch_tfs.items():
                url_id = self.get_url_id(url)
                file_id = self.get_file_id(file_path)
                for token, tf in tokens.items():
                    partial_index[token].append(Posting(url_id, tf))
                pbar.update(1)
            pbar.close()
        
        # Write to binary file with custom format
        filename = f'partial_index_{partial_index_count}.bin'
        token_positions = {}
        with open(filename, 'wb') as f_out:
            with tqdm(total=len(partial_index), desc="Writing partial index to disk", leave=False) as pbar:
                for token in sorted(partial_index.keys()):
                    token_positions[token] = f_out.tell()
                    # Write token and postings (postings converted to dicts)
                    pickle.dump((token, [vars(p) for p in partial_index[token]]), f_out)
                    pbar.update(1)
                pbar.close()
        # Save token positions separately for O(1) lookup later
        index_filename = f'partial_index_{partial_index_count}_index.pkl'
        with open(index_filename, 'wb') as idx_file:
            pickle.dump(token_positions, idx_file)
        
        return filename

    def _initialize_file_iterators(self, files: List[str], merge_pbar):
        """Initialize file iterators for each partial index file in binary mode"""
        file_iters = []
        for fname in files:
            fp = open(fname, 'rb')
            try:
                token, postings = pickle.load(fp)
                file_iters.append((token, postings, fp))
                merge_pbar.update(1)
            except EOFError:
                fp.close()
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

    def _write_current_token(self, outfile, current_token, current_postings, first_token, token_positions):
        """
        Write the current token and its postings to the output file.
        Also track the byte position of each token.
        """
        if not first_token:
            outfile.write(',')
        
        # Record position before writing the token
        token_position = outfile.tell()
        token_positions[current_token] = token_position
        
        json.dump(current_token, outfile)
        outfile.write(':')
        json.dump(current_postings, outfile)

    def merge_partial_indexes(self, partial_index_count: int):
        """Merge partial indexes using a k-way merge without loading everything into memory."""
        self.save_url_mapping()
        self.save_file_mapping()

        files = [f'partial_index_{i}.bin' for i in range(0, partial_index_count)]
        merge_pbar = tqdm(total=partial_index_count, desc="Merging partial indexes", leave=False)

        file_iters = self._initialize_file_iterators(files, merge_pbar)
        
        merge_pbar.reset()
        merge_pbar.set_description("Processing tokens")
        merge_pbar.total = None

        heap, counter = self._initialize_heap(file_iters)
        
        # Dictionary to store token positions in the binary index file
        token_positions = {}

        with open('index.bin', 'wb') as outfile:
            first_token = True
            current_token = None
            current_postings = []

            while heap:
                token, _, postings, fp = heapq.heappop(heap)
                
                if current_token is None or token != current_token:
                    if current_token is not None:
                        # Record position before writing the token
                        token_position = outfile.tell()
                        token_positions[current_token] = token_position
                        
                        # Pickle the token and its postings
                        pickle.dump((current_token, current_postings), outfile)
                    
                    current_token = token
                    current_postings = postings
                else:
                    current_postings.extend(postings)

                try:
                    token, postings = pickle.load(fp)
                    heapq.heappush(heap, (token, counter, postings, fp))
                    counter += 1
                except EOFError:
                    fp.close()

            if current_token is not None:
                # Record position for the last token
                token_position = outfile.tell()
                token_positions[current_token] = token_position
                
                # Pickle the last token and its postings
                pickle.dump((current_token, current_postings), outfile)

        merge_pbar.close()
        
        # Save token positions to a separate file using pickle
        print("Saving token positions for fast lookup...")
        with open('token_positions.pkl', 'wb') as f:
            pickle.dump(token_positions, f)

        # Clean up temporary binary partial index files and their token index files
        for fname in files:
            os.remove(fname)
            index_fname = fname.replace('.bin', '_index.pkl')
            os.remove(index_fname)
