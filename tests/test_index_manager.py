import unittest
import json
import os
from index_manager import IndexManager
from collections import defaultdict

class TestIndexManager(unittest.TestCase):
    def test_get_url_id(self):
        """Test generating and retrieving URL IDs"""
        index_manager = IndexManager()
        
        # First URL should get ID 0
        url_id = index_manager.get_url_id("doc1.test")
        self.assertEqual(url_id, 0)
        
        # Same URL should return same ID
        url_id_again = index_manager.get_url_id("doc1.test")
        self.assertEqual(url_id_again, 0)
        
        # Different URL should get new ID
        another_url_id = index_manager.get_url_id("doc2.test")
        self.assertEqual(another_url_id, 1)

    def test_save_url_mapping(self):
        """Test saving URL to ID mapping"""
        index_manager = IndexManager()
        index_manager.get_url_id("doc1.test")
        index_manager.save_url_mapping()
        
        try:
            with open("urls.json", "r") as f:
                url_mapping = json.load(f)
                
            self.assertIn("0", url_mapping)
            self.assertEqual(url_mapping["0"], "doc1.test")
        finally:
            # Clean up
            if os.path.exists("urls.json"):
                os.remove("urls.json")

    def test_create_partial_index(self):
        """Test creating a partial index from term frequencies"""
        index_manager = IndexManager()
        
        # Simple batch of term frequencies
        batch_tfs = {
            "doc1.test": {"apple": 2, "banana": 1},
            "doc2.test": {"apple": 1, "cherry": 3}
        }
        
        partial_index = index_manager.create_partial_index(batch_tfs)
        
        # Check structure of the partial index
        self.assertIn("apple", partial_index)
        self.assertIn("banana", partial_index)
        self.assertIn("cherry", partial_index)
        
        # Check that the postings are correct
        self.assertEqual(len(partial_index["apple"]), 2)  # Should have 2 docs with "apple"
        self.assertEqual(len(partial_index["banana"]), 1)  # Should have 1 doc with "banana"
        self.assertEqual(len(partial_index["cherry"]), 1)  # Should have 1 doc with "cherry"

    def test_merge_partial_indexes(self):
        """Test merging partial indexes"""
        index_manager = IndexManager()
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
            index_manager.get_url_id("doc1.test")  # id 0
            index_manager.get_url_id("doc2.test")  # id 1
            
            # Merge the partial indexes
            index_manager.merge_partial_indexes(2)
            
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
        """Test writing TF-IDF index"""
        # This test requires a more complex setup with real data
        # For simplicity, we'll just test that the method exists and runs
        index_manager = IndexManager()
        
        # Create a simple index.json first
        simple_index = {
            "test": [{"doc_id": 0, "tf": 1}],
            "word": [{"doc_id": 0, "tf": 2}, {"doc_id": 1, "tf": 1}]
        }
        
        try:
            with open("index.json", "w") as f:
                json.dump(simple_index, f)
                
            # Run the method and check it doesn't crash
            try:
                index_manager.write_tfidf_index(2)  # 2 documents total
                
                # Verify tfidf.json was created
                self.assertTrue(os.path.exists("tfidf.json"))
                
                # Check basic structure of the file
                with open('tfidf.json', 'r') as f:
                    tfidf_index = json.load(f)
                    
                self.assertIn("test", tfidf_index)
                self.assertIn("word", tfidf_index)
                
                # Check that tf is replaced with tfidf
                self.assertIn("tfidf", tfidf_index["test"][0])
                self.assertNotIn("tf", tfidf_index["test"][0])
                
            except Exception as e:
                self.fail(f"write_tfidf_index raised an exception: {str(e)}")
                
        finally:
            # Clean up
            for fname in ["index.json", "tfidf.json"]:
                if os.path.exists(fname):
                    os.remove(fname)
