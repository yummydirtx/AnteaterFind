from index import InvertedIndex
import unittest

class TestIndex(unittest.TestCase):
    def test_tokenize(self):
        index = InvertedIndex()
        self.assertEqual(index.tokenize("<html><body><p>This is a test.</p></body></html>"), {"thi": 1, "is": 1, "a": 1, "test": 1})
        self.assertEqual(index.tokenize("<html><body><p>This is a test. This is only a test.</p></body></html>"), {"thi": 2, "is": 2, "a": 2, "test": 2, "onli": 1})
    
    def test_tokenize_documents(self):
        index = InvertedIndex()
        index.documents = {"doc1": "<html><body><p>This is a test.</p></body></html>", "doc2": "<html><body><p>This is only a test.</p></body></html>"}
        self.assertEqual(index.tokenize_documents(), {"doc1": {"thi": 1, "is": 1, "a": 1, "test": 1}, "doc2": {"thi": 1, "is": 1, "a": 1, "test": 1, "onli": 1}})

    def test_calculate_tfs(self):
        index = InvertedIndex()
        self.assertEqual(index.calculate_tfs({"thi": 1, "is": 1, "a": 1, "test": 1}), {"thi": 0.25, "is": 0.25, "a": 0.25, "test": 0.25})
        self.assertEqual(index.calculate_tfs({"thi": 2, "is": 2, "a": 2, "test": 3, "onli": 1}), {"thi": 0.2, "is": 0.2, "a": 0.2, "test": 0.3, "onli": 0.1})

    def test_calculate_idfs(self):
        index = InvertedIndex()
        index.documents = {"doc1.test": "<html><body><p>This is a test.</p></body></html>", "doc2.test": "<html><body><p>This is only a test.</p></body></html>"}
        document_tokens = index.tokenize_documents()
        self.assertEqual(index.calculate_idfs(document_tokens), {"thi": 0.0, "is": 0.0, "a": 0.0, "test": 0.0, "onli": 0.30102999566398114})

    def test_calculate_tf_idfs(self):
        index = InvertedIndex('zips/dummy.zip')
        self.assertEqual(index.calculate_tf_idfs(), {"doc1.test": {"thi": 0.0, "is": 0.0, "a": 0.0, "test": 0.0}, "doc2.test": {"thi": 0.0, "is": 0.0, "a": 0.0, "test": 0.0, "onli": 0.06020599913279623}})
    
    def test_load_zip(self):
        index = InvertedIndex('zips/dummy.zip')
        self.assertEqual(index.documents, {"doc1.test": "<html><body><p>This is a test.</p></body></html>", "doc2.test": "<html><body><p>This is only a test.</p></body></html>"})
