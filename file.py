import zipfile
import os
import json

class FileOpener:
    def __init__(self, zipPath):
        """intialize zip"""
        self.zipPath = zipPath

    def read_zip(self):
        """Read files from the ZIP without extracting them"""
        # Check if the file is a valid ZIP file
        if not zipfile.is_zipfile(self.zipPath):
            raise zipfile.BadZipFile("The file is not a valid ZIP.")

        documents = {}  # Dictionary to store JSON data

        # Open the ZIP file
        with zipfile.ZipFile(self.zipPath, 'r') as zipfolder:
            for file_name in zipfolder.namelist():
                try:
                    with zipfolder.open(file_name) as file:
                        # Load the entire JSON file
                        #may need to read line by line
                        json_data = json.load(file)  #  the whole file
                        documents[file_name] = json_data  # Store it in the dictionary
                except json.JSONDecodeError:
                    print(f"invalid JSON file: {file_name}")
#json data
        return documents





