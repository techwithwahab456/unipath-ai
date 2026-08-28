from src.rag.rag_file import ask_question


question = "What English language requirement is needed?"


filters = {
    "university": "University One",
}


result = ask_question(
    question=question,
    filters=filters,
    n_results=5,
)


print("\n========================")
print("QUESTION")
print("========================")

print(question)


print("\n========================")
print("AI ANSWER")
print("========================")

print(result["answer"])


print("\n========================")
print("SOURCES")
print("========================")

for source in result["sources"]:
    print(source)


print("\n========================")
print("DISTANCES")
print("========================")

print(result["distances"])