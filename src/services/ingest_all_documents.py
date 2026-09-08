import os

from src.rag.ingest import ingest_pdf


DOCUMENTS_DIR = "./documents"


DOCUMENTS = [
    {
        "filename": "01-Paris-Saclay-M1-AI.pdf",
        "university": "Université Paris-Saclay",
        "country": "France",
        "program": "Master 1 Artificial Intelligence",
        "degree_level": "Master 1",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "02-Paris-Saclay-M2-AI.pdf",
        "university": "Université Paris-Saclay",
        "country": "France",
        "program": "Master 2 Artificial Intelligence",
        "degree_level": "Master 2",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "03-Paris-Saclay-M1-CNS.pdf",
        "university": "Université Paris-Saclay",
        "country": "France",
        "program": "Master 1 Computer and Network Systems",
        "degree_level": "Master 1",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "04-Lille-Master-Info.pdf",
        "university": "Université de Lille",
        "country": "France",
        "program": "Master Informatique",
        "degree_level": "Master",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "05-Nantes-ALMA.pdf",
        "university": "Nantes Université",
        "country": "France",
        "program": "Master Informatique - ALMA",
        "degree_level": "Master",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "07-Rennes-IL.pdf",
        "university": "Université de Rennes",
        "country": "France",
        "program": "Master Informatique - Ingénierie Logicielle",
        "degree_level": "Master",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "08-Toulouse-SDL.pdf",
        "university": "Université Toulouse III",
        "country": "France",
        "program": "Master Informatique - Sciences du Logiciel",
        "degree_level": "Master",
        "intake": "2026",
        "document_type": "admission_requirements",
    },
    {
        "filename": "30-Universities-France-SE-IT-Flutter-LowMath-2027.pdf",
        "university": "Multiple French Universities",
        "country": "France",
        "program": "Software Engineering / IT / Flutter-friendly Programs",
        "degree_level": "Master",
        "intake": "2027",
        "document_type": "university_recommendations",
    },
]


def ingest_all_documents():

    total_chunks = 0
    successful_documents = 0
    failed_documents = 0

    print("=" * 60)
    print("UNIPATH AI - BATCH DOCUMENT INGESTION")
    print("=" * 60)

    for document in DOCUMENTS:

        filename = document["filename"]
        file_path = os.path.join(DOCUMENTS_DIR, filename)

        print("\n" + "-" * 60)
        print(f"Processing: {filename}")

        # Check file exists
        if not os.path.isfile(file_path):
            print(f"ERROR: File not found: {file_path}")
            failed_documents += 1
            continue

        try:

            chunks = ingest_pdf(
                filename=filename,
                file_path=file_path,
                university=document["university"],
                country=document["country"],
                program=document["program"],
                degree_level=document["degree_level"],
                intake=document["intake"],
                document_type=document["document_type"],
            )

            if chunks > 0:
                total_chunks += chunks
                successful_documents += 1
            else:
                failed_documents += 1

        except Exception as e:

            print(f"ERROR while ingesting {filename}")
            print(f"Reason: {e}")

            failed_documents += 1

    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)

    print(f"Documents configured:  {len(DOCUMENTS)}")
    print(f"Successful documents:  {successful_documents}")
    print(f"Failed documents:      {failed_documents}")
    print(f"Total chunks stored:   {total_chunks}")

    print("=" * 60)


if __name__ == "__main__":
    ingest_all_documents()