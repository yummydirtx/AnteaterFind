import zipfile
import json

class FileOpener:
    def __init__(self, zipPath: str):
        """intialize zip"""
        self.zipPath = zipPath
        self.seenUrls = set()

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
            for file_name in zipfolder.namelist():
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
                    except json.JSONDecodeError:
                        print(f"invalid JSON file: {file_name}")

        return url_to_content

    def write_batch_to_index(self, batch_data: dict):
        """
        Writes a batch of data to index.json
        param batch_data: Dictionary containing the batch data to write
        """
        with open('index.json', 'a+') as f:
            f.seek(0)  # Go to start of file
            is_empty = f.read(1) == ''  # Check if file is empty
            
            if is_empty:  # If file is empty, start with [
                f.write('[')
            elif f.tell() > 1:  # If file has content, remove ] and add comma
                f.seek(f.tell() - 2)  # Move before the last ']'
                f.write(',')
            
            json_str = json.dumps(batch_data)
            f.write(json_str)
            f.write(']')
