import unittest
import os
from InvertedIndex.file import FileOpener


class TestFile(unittest.TestCase):
    def test_read_zip(self):
        zip_file_path = os.path.abspath(os.path.join("..", "zips", "dummy.zip"))
        file_opener = FileOpener(zip_file_path)
        documents = file_opener.read_zip()
        found_files = [filename for _, filename in documents.keys()]
        self.assertIn("dummy/doc1.json", found_files)

    def test_read_zip_count(self):
        zip_file_path = os.path.abspath(os.path.join("..", "zips", "dummy.zip"))
        file_opener = FileOpener(zip_file_path)
        documents = file_opener.read_zip()
        self.assertEqual(len(documents), 2)

    def test_delegation_methods(self):
        """Test that FileOpener correctly delegates to other classes"""
        zip_file_path = os.path.abspath(os.path.join("..", "zips", "dummy.zip"))
        file_opener = FileOpener(zip_file_path)

        # Just ensuring these methods don't raise exceptions
        # Actual functionality is tested in the respective test classes
        try:
            # Getting an ID for url mapping delegation test
            self.assertEqual(file_opener.index_manager.get_url_id("test_url"), 0)

            # Just verify these methods exist and are accessible
            self.assertTrue(hasattr(file_opener, 'save_partial_index'))
            self.assertTrue(hasattr(file_opener, 'merge_partial_indexes'))
        #        self.assertTrue(hasattr(file_opener, 'write_tfidf_index'))
        except Exception as e:
            self.fail(f"Delegation methods raised exception: {str(e)}")
