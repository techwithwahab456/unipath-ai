
from collections import Counter


def count_categories(
    programs: list[dict],
) -> dict:
    """
    Count how many programs belong to each
    recommendation category.
    """

    categories = Counter(
        program.get(
            "category",
            "Unknown",
        )
        for program in programs
    )

    return {
        "Dream": categories.get("Dream", 0),
        "Target": categories.get("Target", 0),
        "Safe": categories.get("Safe", 0),
        "Unknown": categories.get("Unknown", 0),
    }


def classify_application_strategy(
    programs: list[dict],
) -> str:
    """
    Determine the overall application strategy
    from the distribution of Dream, Target and Safe
    programs.
    """

    counts = count_categories(programs)

    dream = counts["Dream"]
    target = counts["Target"]
    safe = counts["Safe"]

    total = dream + target + safe

    if total == 0:
        return "No suitable programs identified"

    # A balanced application portfolio.
    if (
        dream >= 1
        and target >= 1
        and safe >= 1
    ):
        return "Balanced Strategy"

    # Too many ambitious programs.
    if dream > target + safe:
        return "High-Risk Strategy"

    # Mostly realistic programs.
    if target >= dream and target >= safe:
        return "Target-Focused Strategy"

    # Mostly safer programs.
    if safe > dream + target:
        return "Conservative Strategy"

    return "Mixed Strategy"


def calculate_category_percentages(
    programs: list[dict],
) -> dict:
    """
    Calculate the percentage distribution of
    Dream, Target and Safe programs.
    """

    counts = count_categories(programs)

    total = (
        counts["Dream"]
        + counts["Target"]
        + counts["Safe"]
    )

    if total == 0:
        return {
            "Dream": 0.0,
            "Target": 0.0,
            "Safe": 0.0,
        }

    return {
        "Dream": round(
            counts["Dream"] / total * 100,
            2,
        ),
        "Target": round(
            counts["Target"] / total * 100,
            2,
        ),
        "Safe": round(
            counts["Safe"] / total * 100,
            2,
        ),
    }


def build_strategy_reason(
    programs: list[dict],
    strategy: str,
) -> str:
    """
    Explain why the application portfolio received
    its strategy classification.
    """

    counts = count_categories(programs)

    dream = counts["Dream"]
    target = counts["Target"]
    safe = counts["Safe"]

    if strategy == "Balanced Strategy":
        return (
            f"The application portfolio contains "
            f"{dream} Dream, {target} Target, and "
            f"{safe} Safe programs. This provides a "
            f"mix of ambitious, realistic, and lower-risk "
            f"options."
        )

    if strategy == "High-Risk Strategy":
        return (
            f"The portfolio contains {dream} Dream "
            f"programs compared with {target} Target "
            f"and {safe} Safe programs. The portfolio "
            f"is heavily concentrated on ambitious "
            f"options."
        )

    if strategy == "Target-Focused Strategy":
        return (
            f"The portfolio is mainly composed of "
            f"{target} Target programs, with {dream} "
            f"Dream and {safe} Safe programs. The "
            f"strategy is focused on realistic options."
        )

    if strategy == "Conservative Strategy":
        return (
            f"The portfolio contains {safe} Safe "
            f"programs compared with {dream} Dream "
            f"and {target} Target programs. The "
            f"application strategy is conservative."
        )

    return (
        f"The portfolio contains {dream} Dream, "
        f"{target} Target, and {safe} Safe programs."
    )


def select_priority_programs(
    programs: list[dict],
    max_programs: int = 3,
) -> list[dict]:
    """
    Select the highest-ranked programs as the
    student's application priorities.

    Programs are expected to already contain a rank
    or score.
    """

    sorted_programs = sorted(
        programs,
        key=lambda program: (
            program.get("rank", 9999),
            -program.get("score", 0),
        ),
    )

    return sorted_programs[:max_programs]


def build_application_distribution(
    programs: list[dict],
) -> dict:
    """
    Build a simple application distribution summary.
    """

    counts = count_categories(programs)

    return {
        "dream_programs": [
            program
            for program in programs
            if program.get("category") == "Dream"
        ],
        "target_programs": [
            program
            for program in programs
            if program.get("category") == "Target"
        ],
        "safe_programs": [
            program
            for program in programs
            if program.get("category") == "Safe"
        ],
    }


def build_admission_strategy(
    programs: list[dict],
    priority_limit: int = 3,
) -> dict:
    """
    Build the complete admission strategy.

    Input:
        Ranked/categorized program results.

    Output:
        Strategy classification,
        category distribution,
        priority programs,
        and explanation.
    """

    strategy = classify_application_strategy(
        programs
    )

    counts = count_categories(programs)

    percentages = calculate_category_percentages(
        programs
    )

    priorities = select_priority_programs(
        programs=programs,
        max_programs=priority_limit,
    )

    distribution = build_application_distribution(
        programs
    )

    reason = build_strategy_reason(
        programs=programs,
        strategy=strategy,
    )

    return {
        "strategy": strategy,
        "category_counts": counts,
        "category_percentages": percentages,
        "priority_programs": priorities,
        "distribution": distribution,
        "reason": reason,
    }


if __name__ == "__main__":

    sample_programs = [
        {
            "rank": 1,
            "university": "University A",
            "program": "Artificial Intelligence",
            "score": 88,
            "category": "Dream",
        },
        {
            "rank": 2,
            "university": "University B",
            "program": "Software Engineering",
            "score": 76,
            "category": "Target",
        },
        {
            "rank": 3,
            "university": "University C",
            "program": "Computer Science",
            "score": 72,
            "category": "Target",
        },
        {
            "rank": 4,
            "university": "University D",
            "program": "Computer Science",
            "score": 58,
            "category": "Safe",
        },
        {
            "rank": 5,
            "university": "University E",
            "program": "Information Technology",
            "score": 52,
            "category": "Safe",
        },
    ]

    result = build_admission_strategy(
        programs=sample_programs,
        priority_limit=3,
    )

    print("\nADMISSION STRATEGY")
    print("=" * 60)

    print(
        f"Strategy: "
        f"{result['strategy']}"
    )

    print("\nCategory Counts:")
    print(
        result["category_counts"]
    )

    print("\nCategory Percentages:")
    print(
        result["category_percentages"]
    )

    print("\nPriority Programs:")

    for program in result["priority_programs"]:

        print(
            f"{program['rank']}. "
            f"{program['university']} | "
            f"{program['program']} | "
            f"{program['category']} | "
            f"{program['score']}"
        )

    print("\nReason:")
    print(result["reason"])

    print("=" * 60)

