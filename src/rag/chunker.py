from langchain_text_splitters import RecursiveCharacterTextSplitter
def split_text(text):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks=splitter.split_text(text)
    
    return chunks
if __name__ == "__main__":
    from document_loader import load_pdf

    pdf_path = "documents/sample.pdf"

    text = load_pdf(pdf_path)

    chunks = split_text(text)

    print(f"Total chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk)    