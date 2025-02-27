import unittest
import zipfile
from InvertedIndex.zip_handler import ZipHandler

class TestZipHandler(unittest.TestCase):
    def test_check_zip_file(self):
        """Test that checking a valid zip file works"""
        try:
            ZipHandler.check_zip_file("zips/dummy.zip")
        except zipfile.BadZipFile:
            self.fail("check_zip_file raised BadZipFile for a valid zip")
        
        # Test with an invalid zip
        with self.assertRaises(zipfile.BadZipFile):
            ZipHandler.check_zip_file("tests/test_zip_handler.py")  # Not a zip file

    def test_get_json_file_list(self):
        """Test retrieving JSON files from a ZIP"""
        json_files = ZipHandler.get_json_file_list("zips/dummy.zip")
        self.assertEqual(json_files, ["dummy/doc1.json", "dummy/doc2.json"])
    
    def test_parse_json_file(self):
        """Test parsing JSON content from a ZIP file"""
        with zipfile.ZipFile("zips/dummy.zip", 'r') as zipfolder:
            results = list(ZipHandler.parse_json_file(zipfolder, "dummy/doc1.json"))
            
            # Should have at least one URL, content pair
            self.assertTrue(len(results) > 0)
            
            # Check structure of results
            for url, content in results:
                self.assertIsInstance(url, str)
                self.assertIsInstance(content, str)
