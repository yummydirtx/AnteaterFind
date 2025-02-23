#from file import FileOpener
from index import InvertedIndex
def generate_m1_report():
    index = InvertedIndex(r"zips/dummy.zip") #test
    numDocuments = len(index.documents) #can call directly from invertedindex bc its calling from file.py
    uniqueTokens = index.get_unique_tokens()
    numUniqueTokens = len(uniqueTokens)

    with open("M1Report.txt", 'w') as f:
        f.write(f"The number of indexed documents: {numDocuments}\n")
        f.write(f"The number of unique words: {numUniqueTokens}\n")
        f.write(f"The total size (in KB) of index on disk:")

if __name__ == "__main__":
    generate_m1_report()
