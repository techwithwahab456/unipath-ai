import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.rag.retriever import retrieve_documents


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


def ask_question(
    question: str,
    n_results: int = 5,
    filters: dict | None = None,
) -> str:

    # 1. Retrieve relevant chunks
    results = retrieve_documents(
        question=question,
        n_results=n_results,
        filters=filters,
    )

    # 2. Extract documents
    documents = results.get("documents", [[]])[0]

    # 3. Check if documents exist
    if not documents:
        return (
            "I don't know based on the available "
            "university documents."
        )

    # 4. Extract metadata
    metadatas = results.get("metadatas", [[]])[0]

    # 5. Combine chunks into context
    context = "\n\n".join(documents)

    # 6. Create prompt
    prompt = f"""
You are UniPath AI, an intelligent university admission assistant.

Answer the user's question using ONLY the information
provided in the university document context below.

Rules:
- Do not use outside knowledge.
- Do not invent requirements.
- If the answer is not available in the context, say exactly:
"I don't know based on the available university documents."
- Give a clear and concise answer.

University Document Context:
{context}

User Question:
{question}

Answer:
"""

    # 7. Ask Gemini
    response = llm.invoke(prompt)

    # 8. Extract response
    content = response.content

    if isinstance(content, list):

        answer = ""

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                answer += item.get("text", "")

        return answer

    return str(content)