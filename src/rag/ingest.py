from src.rag.document_loader import load_pdf
from src.rag.chunker import split_text
from src.rag.embeddings import create_embeddings
from src.rag.vector_store import get_collection


def ingest_pdf(
    filename: str,
    file_path: str,
    university: str,
    country: str,
    program: str,
    degree_level: str,
    intake: str,
    document_type: str,
):

    # 1. Load PDF
    print("Loading PDF...")

    text = load_pdf(file_path)

    if not text.strip():
        print(f"No text extracted from {filename}. Skipping ingestion.")
        return 0

    print(f"Text extracted successfully.")

    # 2. Split text into chunks
    print("Splitting text into chunks...")

    chunks = split_text(text)

    print(f"Total chunks created: {len(chunks)}")

    # 3. Create embeddings
    print("Creating embeddings...")

    embeddings = create_embeddings(chunks)

    print(f"Total embeddings created: {len(embeddings)}")

    # 4. Connect to ChromaDB
    print("Connecting to ChromaDB...")

    collection = get_collection()

    # 5. Create unique IDs
    ids = [
        f"{filename}_chunk_{i}"
        for i in range(len(chunks))
    ]

    # 6. Add metadata to every chunk
    metadatas = [
        {
            "source": filename,
            "university": university,
            "country": country,
            "program": program,
            "degree_level": degree_level,
            "intake": intake,
            "document_type": document_type,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    # 7. Store chunks in ChromaDB
    print("Storing chunks in ChromaDB...")

    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    print("\nDocument ingested successfully!")
    print(f"University: {university}")
    print(f"Program: {program}")
    print(f"Total chunks stored: {len(chunks)}")

    return len(chunks)