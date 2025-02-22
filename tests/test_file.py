from file import FileOpener
import unittest

class TestFile(unittest.TestCase):
    def test_read_zip(self):
        file_opener = FileOpener("zips/analyst.zip")
        documents = file_opener.read_zip()
        self.assertIn("https://www.informatics.uci.edu/rolling-stone-how-developers-can-reduce-toxicity-in-online-communities-ph-d-student-katherine-lo-quoted/", documents)