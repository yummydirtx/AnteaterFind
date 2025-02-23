from file import FileOpener
def generate_m1_report():
    openFile = FileOpener(r"zips/developer.zip")
    readZip = openFile.read_zip()
    with open("M1Report.txt", 'w') as f:
        f.write(f"Number of documents: {len(readZip)}\n")

if __name__ == "__main__":
    generate_m1_report()
