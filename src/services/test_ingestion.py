from src.models.university_document import UniversityDocument
from src.services.document_ingestion_service import (
    ingest_university_document,
)


document = UniversityDocument(
    filename="sample.pdf",
    file_path="documents/sample.pdf",
    university="University One",
    country="France",
    program="Master in Artificial Intelligence",
    degree_level="Master",
    intake="Fall 2027",
    document_type="admission_requirements",
)


chunks_stored = ingest_university_document(document)


print("\n========================")
print("INGESTION TEST COMPLETE")
print("========================")

print(f"Chunks stored: {chunks_stored}")