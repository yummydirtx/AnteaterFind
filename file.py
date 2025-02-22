import zipfile
import json

class FileOpener:
    def __init__(self, zipPath: str):
        """intialize zip"""
        self.zipPath = zipPath

    def read_zip(self) -> dict:
        """Read files from the ZIP and return a dict mapping urls to content"""
        if not zipfile.is_zipfile(self.zipPath):
            raise zipfile.BadZipFile("The file is not a valid ZIP.")

        # Dictionary to store url -> content mapping
        url_to_content = {}

        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            for file_name in zipfolder.namelist():
                if file_name.startswith("DEV/") and file_name.endswith(".json"):
                    try:
                        with zipfolder.open(file_name) as file:
                            json_data = json.load(file)
                            # Only add entries that have both url and content
                            if 'url' in json_data and 'content' in json_data:
                                url_to_content[json_data['url']] = json_data['content']
                    except json.JSONDecodeError:
                        print(f"invalid JSON file: {file_name}")

        return url_to_content
