from src.config.llm import llm


def test_llm():

    response = llm.invoke(
        """
You are UniPath AI.

Briefly explain what you can do for a student
applying for a Master's degree in Artificial Intelligence.
"""
    )

    print("\n--- AI RESPONSE ---\n")
    print(response.content)


if __name__ == "__main__":
    test_llm()