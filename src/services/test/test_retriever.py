from src.rag.retriever import retrieve_documents


def print_results(question: str, n_results: int = 5):

    print("\n" + "=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    results = retrieve_documents(
        question=question,
        n_results=n_results,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        print("No documents found.")
        return

    for i, document in enumerate(documents):

        metadata = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else None

        print("\n" + "-" * 80)
        print(f"RESULT {i + 1}")

        print(f"Source:      {metadata.get('source', 'Unknown')}")
        print(f"University:  {metadata.get('university', 'Unknown')}")
        print(f"Program:     {metadata.get('program', 'Unknown')}")
        print(f"Country:     {metadata.get('country', 'Unknown')}")
        print(f"Degree:      {metadata.get('degree_level', 'Unknown')}")
        print(f"Intake:      {metadata.get('intake', 'Unknown')}")
        print(f"Doc Type:    {metadata.get('document_type', 'Unknown')}")
        print(f"Chunk:       {metadata.get('chunk_index', 'Unknown')}")
        print(f"Distance:    {distance}")

        print("\nRetrieved Text:")
        print(document)


def main():

    questions = [

        "What are the English language requirements for Paris-Saclay M1 Artificial Intelligence?",

        "What mathematics are required for Artificial Intelligence programs?",

        "What documents are required for a Master's application?",

        "What are the admission requirements for Computer Science programs in France?",

        "Which programs are suitable for a student with a Computer Science background?",

    ]

    for question in questions:

        print_results(
            question=question,
            n_results=5,
        )


if __name__ == "__main__":
    main()