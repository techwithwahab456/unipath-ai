from src.rag.vector_store import get_collection


def delete_sample_document():

    print("=" * 60)
    print("REMOVING TEST DOCUMENT")
    print("=" * 60)

    # Connect to ChromaDB
    collection = get_collection()

    # Find all chunks/documents belonging to sample.pdf
    results = collection.get(
        where={
            "source": "sample.pdf"
        }
    )

    ids = results.get("ids", [])

    if not ids:
        print("\nNo sample.pdf document found in ChromaDB.")
        return

    print(f"\nFound {len(ids)} sample.pdf document(s).")

    # Delete only sample.pdf
    collection.delete(
        ids=ids
    )

    print("\nsample.pdf deleted successfully!")
    print(f"Deleted documents: {len(ids)}")

    print("=" * 60)


if __name__ == "__main__":
    delete_sample_document()