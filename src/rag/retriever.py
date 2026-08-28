from src.rag.embeddings import create_embedding
from src.rag.vector_store import get_collection


def retrieve_documents(
    question: str,
    n_results: int = 5,
    filters: dict | None = None,
):

    # 1. Convert question into embedding
    query_embedding = create_embedding(question)

    # 2. Connect to ChromaDB
    collection = get_collection()

    # 3. Prepare query arguments

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    # 4. Add metadata filters if provided
    if filters:
        query_args["where"] = filters

    # 5. Search ChromaDB
    results = collection.query(**query_args)

    return results