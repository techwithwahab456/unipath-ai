from src.rag.vector_store import get_collection


def get_available_programs() -> list[dict]:
    """
    Get all unique university/program combinations
    currently stored in ChromaDB.

    Returns:
        A list of unique program dictionaries.
    """

    collection = get_collection()

    results = collection.get(
        include=["metadatas"]
    )

    metadatas = results.get("metadatas", [])

    programs = []
    seen = set()

    for metadata in metadatas:

        if not metadata:
            continue

        university = metadata.get("university")
        program = metadata.get("program")

        if not university or not program:
            continue

        key = (
            university,
            program,
            metadata.get("country", "Unknown"),
            metadata.get("degree_level", "Unknown"),
            metadata.get("intake", "Unknown"),
        )

        if key in seen:
            continue

        seen.add(key)

        programs.append(
            {
                "university": university,
                "program": program,
                "country": metadata.get(
                    "country",
                    "Unknown",
                ),
                "degree_level": metadata.get(
                    "degree_level",
                    "Unknown",
                ),
                "intake": metadata.get(
                    "intake",
                    "Unknown",
                ),
            }
        )

    return programs


if __name__ == "__main__":

    programs = get_available_programs()

    print("\nAvailable Programs:")
    print("=" * 60)

    for i, program in enumerate(programs, start=1):

        print(
            f"{i}. "
            f"{program['university']} | "
            f"{program['program']} | "
            f"{program['degree_level']} | "
            f"{program['intake']}"
        )

    print("=" * 60)
    print(f"Total unique programs: {len(programs)}")