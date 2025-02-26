from file import FileOpener
import unittest
import json
import os
from index import InvertedIndex

class TestFile(unittest.TestCase):
    def test_read_zip(self):
        file_opener = FileOpener("zips/dummy.zip")
        documents = file_opener.read_zip()
        self.assertIn("doc1.test", documents)

    def test_get_url_id(self):
        file_opener = FileOpener("zips/dummy.zip")
        url_id = file_opener.get_url_id("doc1.test")
        self.assertEqual(url_id, 0)

    def test_save_url_mapping(self):
        file_opener = FileOpener("zips/dummy.zip")
        file_opener.get_url_id("doc1.test")
        file_opener.save_url_mapping()
        with open("urls.json", "r") as f:
            url_mapping = json.load(f)
        self.assertIn("0", url_mapping)
        self.assertEqual(url_mapping["0"], "doc1.test")

    def test_check_zip_file(self):
        file_opener = FileOpener("zips/dummy.zip")
        self.assertIsNone(file_opener.check_zip_file())

    def test_get_json_file_list(self):
        file_opener = FileOpener("zips/dummy.zip")
        json_files = file_opener.get_json_file_list()
        self.assertEqual(json_files, ["dummy/doc1.json", "dummy/doc2.json"])
    
    def test_read_zip_count(self):
        file_opener = FileOpener("zips/dummy.zip")
        documents = file_opener.read_zip(count=1)
        self.assertEqual(len(documents), 1)
        self.assertIn("doc1.test", documents)

    def test_merge_partial_indexes(self):
        file_opener = FileOpener("zips/dummy.zip")
        test_files = ['partial_index_0.json', 'partial_index_1.json', 'index.json', 'urls.json']
        
        try:
            # Create test partial indexes
            partial_index_0 = [
                {"token": "apple", "postings": [{"doc_id": 0, "tf": 2}]},
                {"token": "banana", "postings": [{"doc_id": 0, "tf": 1}]}
            ]
            
            partial_index_1 = [
                {"token": "apple", "postings": [{"doc_id": 1, "tf": 1}]},
                {"token": "cherry", "postings": [{"doc_id": 1, "tf": 3}]}
            ]
            
            # Write test partial indexes to files
            with open('partial_index_0.json', 'w') as f:
                for entry in partial_index_0:
                    f.write(json.dumps(entry) + '\n')
                    
            with open('partial_index_1.json', 'w') as f:
                for entry in partial_index_1:
                    f.write(json.dumps(entry) + '\n')
            
            # Set up URL mapping
            file_opener.get_url_id("doc1.test")  # id 0
            file_opener.get_url_id("doc2.test")  # id 1
            
            # Merge the partial indexes
            file_opener.merge_partial_indexes(2)
            
            # Verify the merged index
            with open('index.json', 'r') as f:
                merged_index = json.load(f)
                
            # Check merged results
            self.assertEqual(len(merged_index), 3)  # Should have apple, banana, cherry
            self.assertEqual(len(merged_index["apple"]), 2)  # Apple appears in both docs
            self.assertEqual(len(merged_index["banana"]), 1)  # Banana appears in one doc
            self.assertEqual(len(merged_index["cherry"]), 1)  # Cherry appears in one doc
            
            # Verify specific postings
            apple_postings = merged_index["apple"]
            self.assertTrue(any(p["doc_id"] == 0 and p["tf"] == 2 for p in apple_postings))
            self.assertTrue(any(p["doc_id"] == 1 and p["tf"] == 1 for p in apple_postings))
        
        finally:
            # Clean up all generated files
            for fname in test_files:
                if os.path.exists(fname):
                    os.remove(fname)

    def test_write_tfidf_index(self):
        InvertedIndex("zips/dummy.zip")
        with open('tfidf.json', 'r') as f:
            tfidf_index = json.load(f)
        
        self.assertEqual(tfidf_index["onli"][0]['tfidf'], 0.3010299956639812)
