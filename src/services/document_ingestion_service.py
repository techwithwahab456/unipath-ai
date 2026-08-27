from src.models.university_document import UniversityDocument
from src.rag.ingest import ingest_pdf


def ingest_university_document(
    document: UniversityDocument,
):

    print("\nStarting university document ingestion...")

    print(f"University: {document.university}")
    print(f"Program: {document.program}")
    print(f"Country: {document.country}")
    print(f"Document: {document.filename}")

    chunks_stored = ingest_pdf(
        filename=document.filename,
        file_path=document.file_path,
        university=document.university,
        country=document.country,
        program=document.program,
        degree_level=document.degree_level,
        intake=document.intake,
        document_type=document.document_type,
    )

    print("\nIngestion completed.")
    print(f"Chunks stored: {chunks_stored}")

    return chunks_stored