import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.rag.retriever import retrieve_documents


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


# Starting threshold based on our current tests
RELEVANCE_THRESHOLD = 1.25


def ask_question(
    question: str,
    filters: dict | None = None,
    n_results: int = 5,
) -> dict:

    # 1. Retrieve relevant chunks from ChromaDB
    results = retrieve_documents(
        question=question,
        filters=filters,
        n_results=n_results,
    )


    # 2. Extract documents
    documents = results.get("documents", [[]])[0]


    # 3. Extract metadata
    metadatas = results.get("metadatas", [[]])[0]


    # 4. Extract distances
    distances = results.get("distances", [[]])[0]


    # 5. Check whether any documents were retrieved
    if not documents or not distances:

        return {
            "answer": (
                "I don't know based on the available "
                "university documents."
            ),
            "sources": [],
            "distances": [],
        }


    # 6. Check the best retrieved result
    best_distance = distances[0]


    # 7. Reject irrelevant retrieval before calling Gemini
    if best_distance > RELEVANCE_THRESHOLD:

        return {
            "answer": (
                "I don't know based on the available "
                "university documents."
            ),
            "sources": [],
            "distances": distances,
        }


    # 8. Keep only relevant chunks
    relevant_documents = []
    relevant_metadatas = []
    relevant_distances = []


    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        if distance <= RELEVANCE_THRESHOLD:

            relevant_documents.append(document)
            relevant_metadatas.append(metadata)
            relevant_distances.append(distance)


    # 9. Safety check
    if not relevant_documents:

        return {
            "answer": (
                "I don't know based on the available "
                "university documents."
            ),
            "sources": [],
            "distances": distances,
        }


    # 10. Create context from only relevant chunks
    context = "\n\n".join(relevant_documents)


    # 11. Create source information
    sources = []


    for metadata in relevant_metadatas:

        source = {
            "filename": metadata.get("source", "Unknown"),
            "university": metadata.get("university", "Unknown"),
            "program": metadata.get("program", "Unknown"),
            "country": metadata.get("country", "Unknown"),
            "document_type": metadata.get(
                "document_type",
                "Unknown",
            ),
        }


        # Avoid duplicate sources
        if source not in sources:

            sources.append(source)


    # 12. Create the RAG prompt
    prompt = f"""
You are UniPath AI, an intelligent university admission assistant.

Answer the user's question using ONLY the information
provided in the university document context below.

Rules:
- Do not use outside knowledge.
- Do not invent requirements.
- If the answer is not available in the context, say:
  "I don't know based on the available university documents."
- Give a clear and concise answer.

University Document Context:
{context}

User Question:
{question}

Answer:
"""


    # 13. Ask Gemini only when retrieval is relevant
    response = llm.invoke(prompt)


    # 14. Extract Gemini response
    content = response.content


    if isinstance(content, list):

        answer = ""

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):

                answer += item.get("text", "")

    else:

        answer = str(content)


    # 15. Return final result
    return {
        "answer": answer,
        "sources": sources,
        "distances": relevant_distances,
    }