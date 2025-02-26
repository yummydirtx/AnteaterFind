import unittest
from file import FileOpener

class TestFile(unittest.TestCase):
    def test_read_zip(self):
        file_opener = FileOpener("zips/dummy.zip")
        documents = file_opener.read_zip()
        self.assertIn("doc1.test", documents)
    
    def test_read_zip_count(self):
        file_opener = FileOpener("zips/dummy.zip")
        documents = file_opener.read_zip(count=1)
        self.assertEqual(len(documents), 1)
        self.assertIn("doc1.test", documents)
    
    def test_delegation_methods(self):
        """Test that FileOpener correctly delegates to other classes"""
        file_opener = FileOpener("zips/dummy.zip")
        
        # Just ensuring these methods don't raise exceptions
        # Actual functionality is tested in the respective test classes
        try:
            # Getting an ID for url mapping delegation test
            self.assertEqual(file_opener.index_manager.get_url_id("test_url"), 0)
            
            # Just verify these methods exist and are accessible
            self.assertTrue(hasattr(file_opener, 'save_partial_index'))
            self.assertTrue(hasattr(file_opener, 'merge_partial_indexes'))
            self.assertTrue(hasattr(file_opener, 'write_tfidf_index'))
        except Exception as e:
            self.fail(f"Delegation methods raised exception: {str(e)}")
