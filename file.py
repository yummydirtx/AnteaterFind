import zipfile
import json
from tqdm import tqdm

class FileOpener:
    def __init__(self, zipPath: str):
        """intialize zip"""
        self.zipPath = zipPath
        self.seenUrls = set()
        
        # Initialize progress tracking
        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            self.total_files = len([f for f in zipfolder.namelist() if f.endswith('.json')])
            self.pbar = tqdm(total=self.total_files, desc="Processing files")

    def read_zip(self, count: int = None) -> dict:
        """
        Read files from the ZIP and return a dict mapping urls to content
        param count: The number of files to read from the ZIP. If None, read all files.
        return: A dictionary mapping URLs to their content.
        """
        if not zipfile.is_zipfile(self.zipPath):
            raise zipfile.BadZipFile("The file is not a valid ZIP.")

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
                            json_data = json.load(file)
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

    def close(self):
        """Close the progress bar when done processing all files"""
        self.pbar.close()

