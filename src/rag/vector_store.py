import chromadb


VECTORSTORE_PATH = "./vectorstore"
COLLECTION_NAME = "documents"
client=chromadb.PersistentClient(path=VECTORSTORE_PATH)
collection=client.get_or_create_collection(name=COLLECTION_NAME)
def get_collection():
    return collection
if __name__ == "__main__":
    print("ChromaDB connected successfully!")
    print("Collection:", collection.name)
    print("Total documents:", collection.count())