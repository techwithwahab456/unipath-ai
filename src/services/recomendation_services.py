
from src.models.student_profile import StudentProfile
from src.services.ranking_service import rank_programs
from src.services.program_services import get_available_programs


def classify_program(score: float) -> str:
    """
    Classify a program based on its suitability score.

    Score ranges:

    80-100 -> Dream
    65-79  -> Target
    0-64   -> Safe / Backup
    """

    if score >= 80:
        return "Dream"

    if score >= 65:
        return "Target"

    return "Safe"


def build_recommendation_reason(
    program: dict,
) -> str:
    """
    Build a short explanation for why a program
    received its recommendation category.
    """

    score = program["score"]
    risk = program["risk"]
    eligibility = program["eligibility_status"]

    if eligibility.lower() == "eligible":
        eligibility_text = (
            "the available requirements indicate "
            "that the student is eligible"
        )

    elif eligibility.lower() == "partially eligible":
        eligibility_text = (
            "the available requirements indicate "
            "some areas that need further checking"
        )

    elif eligibility.lower() == "not eligible":
        eligibility_text = (
            "the available requirements indicate "
            "that the student does not currently meet "
            "one or more requirements"
        )

    else:
        eligibility_text = (
            "some requirements could not be confirmed "
            "from the available documents"
        )

    return (
        f"This program has a suitability score of "
        f"{score:.0f}/100 and is classified as "
        f"{program['category']}. "
        f"The recommendation is based on the available "
        f"eligibility evidence, where {eligibility_text}. "
        f"Current risk level: {risk}."
    )


def recommend_programs(
    profile: StudentProfile,
    programs: list[dict] | None = None,
) -> list[dict]:
    """
    Generate university recommendations for a student.

    If programs are not supplied, they are automatically
    discovered from ChromaDB.
    """

    if programs is None:
        programs = get_available_programs()

    ranked_programs = rank_programs(
        profile=profile,
        programs=programs,
    )

    recommendations = []

    for program in ranked_programs:

        category = classify_program(
            program["score"]
        )

        recommendation = {
            **program,
            "category": category,
        }

        recommendation["reason"] = (
            build_recommendation_reason(
                recommendation
            )
        )

        recommendations.append(
            recommendation
        )

    return recommendations


if __name__ == "__main__":

    student = StudentProfile(
        name="Abdul Wahab",
        bachelor_degree="BS Computer Science",
        field_of_study="Computer Science",
        university="Islamia University of Bahawalpur",
        cgpa=3.06,
        graduation_year=2026,
        target_degree="Master's",
        target_field="Computer Science / Software Engineering",
        target_countries=["France"],
        skills=[
            "Flutter",
            "Firebase",
            "Python",
            "FastAPI",
            "RAG",
        ],
        projects=[
            "CraftedCuts",
            "UniPath AI",
        ],
        work_experience=[
            "Flutter development",
        ],
        english_test="IELTS",
        english_score=None,
    )

    recommendations = recommend_programs(
        profile=student
    )

    print("\nUNIPATH AI RECOMMENDATIONS")
    print("=" * 70)

    for program in recommendations:

        print(
            f"\n#{program['rank']} "
            f"{program['university']}"
        )

        print(
            f"Program: {program['program']}"
        )

        print(
            f"Score: {program['score']}/100"
        )

        print(
            f"Category: {program['category']}"
        )

        print(
            f"Risk: {program['risk']}"
        )

        print(
            f"Eligibility: "
            f"{program['eligibility_status']}"
        )

        print(
            f"Reason: "
            f"{program['reason']}"
        )

    print("\n" + "=" * 70)

