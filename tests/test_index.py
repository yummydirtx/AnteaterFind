from index import InvertedIndex
import unittest

class TestIndex(unittest.TestCase):
    def test_tokenize(self):
        index = InvertedIndex()
        self.assertEqual(index.tokenize("<html><body><p>This is a test.</p></body></html>"), {"thi": 1, "is": 1, "a": 1, "test": 1})
