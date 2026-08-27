from pypdf import PdfReader
def load_pdf(file_path):
    reader=PdfReader(file_path)
    text=''
    for page in reader.pages:
        reader_text=page.extract_text()
        if reader_text:
           
           text +=reader_text +"\n"
    return text;
if __name__ == "__main__":
    

    

    print("PDF loaded successfully!")    