import zipfile
from tqdm import tqdm
from .zip_handler import ZipHandler
from .index_manager import IndexManager
from urllib.parse import urldefrag
class FileOpener:
    def __init__(self, zipPath: str):
        """Initialize file opener with zip path"""
        self.zipPath = zipPath
        self.seenUrls = set()
        self.index_manager = IndexManager()
        
        # Initialize progress tracking
        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            self.total_files = len([f for f in zipfolder.namelist() if f.endswith('.json')])
            self.pbar = tqdm(total=self.total_files, desc="Processing files")

    def normalize_url(self, url):
        """Remove fragment"""
        #so we dont get the #content type of website
        return urldefrag(url)[0]

    def read_zip(self, count: int = None) -> dict:
        """
        Read files from the ZIP and return a dict mapping urls to content
        param count: The number of files to read from the ZIP. If None, read all files.
        return: A dictionary mapping URLs to their content.
        """
        ZipHandler.check_zip_file(self.zipPath)
        url_to_content = {}
        files_processed = 0

        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            json_files = ZipHandler.get_json_file_list(self.zipPath)

            for file_name in json_files:
                if count is not None and files_processed >= count:
                    break

                for url, content in ZipHandler.parse_json_file(zipfolder, file_name):
                    if count is not None and files_processed >= count:
                        break
                    normalized_url = self.normalize_url(url)
                    if normalized_url not in self.seenUrls:
                        self.seenUrls.add(normalized_url)
                        url_to_content[normalized_url] = content
                        files_processed += 1
                        self.pbar.update(1)

        return url_to_content
    
    def save_partial_index(self, batch_tfs, partial_index_count):
        """Delegate to index manager to save partial index"""
        return self.index_manager.save_partial_index(batch_tfs, partial_index_count)
    
    def merge_partial_indexes(self, partial_index_count: int):
        """Delegate to index manager to merge partial indexes"""
        return self.index_manager.merge_partial_indexes(partial_index_count)

    def close(self):
        """Close the progress bar when done processing all files"""
        self.pbar.close()
