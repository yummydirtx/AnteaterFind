from InvertedIndex.index import InvertedIndex, weighted_tags, tokenize_chunk
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import unittest

#69% coverage for index.py
class TestIndex(unittest.TestCase):
#    def test_tokenize(self):
#        index = InvertedIndex()
#        self.assertEqual(index.tokenize("<html><body><p>This is a test.</p></body></html>"), {"thi": 1, "is": 1, "a": 1, "test": 1})
#        self.assertEqual(index.tokenize("<html><body><p>This is a test. This is only a test.</p></body></html>"), {"thi": 2, "is": 2, "a": 2, "test": 2, "onli": 1})
    
    def test_tokenize_documents(self):
        index = InvertedIndex()
        index.documents = {"doc1": "<html><body><p>This is a test.</p></body></html>", "doc2": "<html><body><p>This is only a test.</p></body></html>"}
        self.assertEqual(index.tokenize_documents(), {"doc1": {"thi": 0.25, "is": 0.25, "a": 0.25, "test": 0.25}, "doc2": {"thi": 0.2, "is": 0.2, "a": 0.2, "test": 0.2, "onli": 0.2}})

    def test_calculate_tfs(self):
        index = InvertedIndex()
        self.assertEqual(index.calculate_tfs({"thi": 1, "is": 1, "a": 1, "test": 1}), {"thi": 0.25, "is": 0.25, "a": 0.25, "test": 0.25})
        self.assertEqual(index.calculate_tfs({"thi": 2, "is": 2, "a": 2, "test": 3, "onli": 1}), {"thi": 0.2, "is": 0.2, "a": 0.2, "test": 0.3, "onli": 0.1})

    def test_weighted_tags(self):
        index = InvertedIndex()
        html = "<html><body><h1>Title</h1><h2>Subtitle</h2><h3>Subtitle 3</h3><b>Bold</b><p>Normal text</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        tokens = weighted_tags(soup)
        expected = ["title", "title", "title", "title", "subtitle", "subtitle", "subtitle","subtitle", "subtitle" ,"3", "3", "bold"]
        self.assertEqual(tokens, expected)


    def test_tokenize_chunk(self):
        stemmer = PorterStemmer()
        chunk = {
            "doc1": "<html><body><h1>Title</h1><p>This is a test.</p></body></html>",
            "doc2": "<html><body><p>This is only a test.</p></body></html>"
        }
        result = tokenize_chunk(chunk, stemmer)

        expected =\
            {'doc1': {'a': 1, 'is': 1, 'test': 1, 'thi': 1, 'titl': 5},
             'doc2': {'a': 1, 'is': 1, 'onli': 1, 'test': 1, 'thi': 1}}
        self.assertEqual(result, expected)
