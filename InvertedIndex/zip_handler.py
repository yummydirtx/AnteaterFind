import zipfile
import json
from typing import Iterator, Tuple

class ZipHandler:
    @staticmethod
    def check_zip_file(zip_path: str) -> None:
        """
        Checks if the zip provided is valid
        Args:
            zip_path (str): path of the ZIP file
        Raises:
            zipfile.BadZipFile: If file is not valid ZIP --error handling
        """
        if not zipfile.is_zipfile(zip_path):
            raise zipfile.BadZipFile("The file is not a valid ZIP.")

    @staticmethod
    def get_json_file_list(zip_path: str) -> list:
        """
        Retrieve list of json files from zip folder
        Args:
            zip_path (str): path of the ZIP file
        Return:
            list: A list of JSON file names
        """
        with zipfile.ZipFile(zip_path, 'r') as zipfolder:
            return [f for f in zipfolder.namelist() if f.endswith('.json')]

    @staticmethod
    def parse_json_file(zipfolder, file_name: str) -> Iterator[Tuple[str, str]]:
        """
        Parse information from a JSON file, yield url and content
        Args:
            zipfolder: Opened zipfile.ZipFile folder object
            file_name (str): name of JSON file
        Yields:
            Iterator[Tuple[str, str]]: A generator that yields tuples of URL and content from the JSON file.
        Raises:
            Exception: Reading file error
        """
        try:
            with zipfolder.open(file_name) as file:
                for line in file:
                    try:
                        json_data = json.loads(line.decode('utf-8'))
                        if 'url' in json_data and 'content' in json_data:
                            yield json_data['url'], json_data['content']
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in file: {file_name}")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
