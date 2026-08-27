from src.rag.retriever import retrieve_documents


question = "What IELTS score is required for admission?"


results = retrieve_documents(
    question=question,
    n_results=3,
)


documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]


print("\nSEARCH RESULTS:\n")


for i in range(len(documents)):

    print(f"--- RESULT {i + 1} ---")

    print("Document:")
    print(documents[i])

    print("\nMetadata:")
    print(metadatas[i])

    print("\nDistance:")
    print(distances[i])

    print("\n" + "=" * 50 + "\n")