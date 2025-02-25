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

    def read_zip(self, count: int = None) -> dict:
        """
        Read files from the ZIP and return a dict mapping urls to content
        param count: The number of files to read from the ZIP. If None, read all files.
        return: A dictionary mapping URLs to their content.
        """

        # Dictionary to store url -> content mapping
        url_to_content = {}
        files_processed = 0

        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            # Get list of JSON files
            json_files = [f for f in zipfolder.namelist() if f.endswith('.json')]

            for file_name in json_files:
                if count is not None and files_processed >= count:
                    break

                if file_name.endswith(".json"):
                    try:
                        with zipfolder.open(file_name) as file:
                            for line in file:
                                json_data = json.loads(line.decode('utf-8'))
                                # Only add entries that have both url and content
                                if 'url' in json_data and 'content' in json_data:
                                    if json_data['url'] not in self.seenUrls:
                                        self.seenUrls.add(json_data['url'])
                                        url_to_content[json_data['url']] = json_data['content']
                                        files_processed += 1
                                        self.pbar.update(1)
                    except json.JSONDecodeError:
                        print(f"invalid JSON file: {file_name}")

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

    def merge_partial_indexes(self, partial_index_count: int):
        """Merge partial indexes using a k-way merge without loading everything into memory."""
        # Save URL mapping first
        self.save_url_mapping()

        files = [f'partial_index_{i}.json' for i in range(0, partial_index_count)]
        merge_pbar = tqdm(total=partial_index_count, desc="Merging partial indexes")

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

        # Reset progress bar for the actual merging process
        merge_pbar.reset()
        merge_pbar.set_description("Processing tokens")

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

        # Close the progress bar
        merge_pbar.close()

        # Remove partial index files
        for fname in files:
            os.remove(fname)

    def close(self):
        """Close the progress bar when done processing all files"""
        self.pbar.close()
