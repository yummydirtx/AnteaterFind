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
