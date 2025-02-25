import zipfile
import json
from tqdm import tqdm
import os
import heapq
from collections import defaultdict
from posting import Posting

class FileOpener:
    def __init__(self, zipPath: str):
        """intialize zip"""
        self.zipPath = zipPath
        self.seenUrls = set()
        self.url_to_id = {}  # Map URLs to numeric IDs
        self.current_url_id = 0

        # Initialize progress tracking
        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            self.total_files = len([f for f in zipfolder.namelist() if f.endswith('.json')])
            self.pbar = tqdm(total=self.total_files, desc="Processing files")

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

    def check_zip_file(self):
        """Checks if the zip provided is valid"""
        if not zipfile.is_zipfile(self.zipPath):
            raise zipfile.BadZipFile("The file is not a valid ZIP.")

    def get_json_file_list(self):
        """Retrieve list of json files from zip folder"""
        # need to probably either in here or in another function verify if its a good one or not
        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            return [f for f in zipfolder.namelist() if f.endswith('.json')]

    def parse_json_file(self, zipfolder, file_name):
        """parse information from a json file, return url, content """
        try:
            with zipfolder.open(file_name) as file:
                for line in file:
                    try:
                        json_data = json.loads(line.decode('utf-8'))
                        if 'url' in json_data and 'content' in json_data:
                            #may consider yield
                            yield json_data['url'], json_data['content']
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in file: {file_name}")
        except Exception as e:
            print(f"Error reading {file_name}")

    def read_zip(self, count: int = None) -> dict:
        """
        Read files from the ZIP and return a dict mapping urls to content
        param count: The number of files to read from the ZIP. If None, read all files.
        return: A dictionary mapping URLs to their content.
        """

        # Dictionary to store url -> content mapping
        self.check_zip_file()
        url_to_content = {}
        files_processed = 0

        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            json_files = self.get_json_file_list()

            for file_name in json_files:
                if count is not None and files_processed >= count:
                    break

                for url, content in self.parse_json_file(zipfolder, file_name):
                    if count is not None and files_processed >= count:
                        break
                    if url not in self.seenUrls:
                        self.seenUrls.add(url)
                        url_to_content[url] = content
                        files_processed += 1
                        self.pbar.update(1)

        return url_to_content

    def save_partial_index(self, batch_tfs: dict, partial_index_count: int):
        """
        Saves a batch of documents as a partial index to disk.
        Each partial index is sorted and contains one token entry per line.
        """
        partial_index = defaultdict(list)
        for url, tokens in batch_tfs.items():
            url_id = self.get_url_id(url)
            for token, tf in tokens.items():
                partial_index[token].append(Posting(url_id, tf))

        filename = f'partial_index_{partial_index_count}.json'
        with open(filename, 'w') as f:
            # Write one token entry per line in sorted order
            for token in sorted(partial_index.keys()):
                entry = {
                    "token": token,
                    "postings": [vars(p) for p in partial_index[token]]
                }
                f.write(json.dumps(entry) + "\n")

    def _initialize_file_iterators(self, files, merge_pbar):
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

        for fname in files:
            os.remove(fname)

    def close(self):
        """Close the progress bar when done processing all files"""
        self.pbar.close()
