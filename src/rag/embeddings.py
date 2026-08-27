from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


model = SentenceTransformer(MODEL_NAME)
def create_embeddings(texts):
    return model.encode(texts).tolist()
def create_embedding(text):
    return model.encode(text).tolist() 
if __name__ == "__main__":
    text = "This is a test sentence."

    embedding = create_embedding(text)

    print("Embedding created successfully!")
    print("Vector dimension:", len(embedding))
    print("First 10 values:", embedding[:10])   