
from src.models.student_profile import StudentProfile
from src.services.comparison_services import compare_programs


def normalize_status(status: str) -> str:
    """
    Normalize eligibility status values.

    Supported statuses from eligibility service:

    Meets
    Likely Meets
    Does Not Meet
    Unknown
    """

    normalized = status.lower().strip()

    if normalized in {
        "meets",
        "eligible",
    }:
        return "meets"

    if normalized in {
        "likely meets",
        "partial",
        "partially eligible",
    }:
        return "likely_meets"

    if normalized in {
        "does not meet",
        "not eligible",
        "not_eligible",
    }:
        return "does_not_meet"

    if normalized == "unknown":
        return "unknown"

    return "unknown"


def calculate_eligibility_score(
    eligibility_result,
) -> float:
    """
    Calculate an eligibility score from 0-100.

    Scoring:

    Meets           = +20
    Likely Meets    = +10
    Unknown         = +5
    Does Not Meet   = -30

    The final score is normalized to 0-100.
    """

    if not eligibility_result.checks:
        return 0.0

    score = 0.0

    for check in eligibility_result.checks:

        status = normalize_status(check.status)

        if status == "meets":
            score += 20

        elif status == "likely_meets":
            score += 10

        elif status == "unknown":
            score += 5

        elif status == "does_not_meet":
            score -= 30

    # Keep score inside 0-100
    score = max(0.0, min(score, 100.0))

    return score


def calculate_program_score(
    eligibility_result,
    profile_match: dict | None = None,
) -> float:
    """
    Calculate the final program suitability score.

    Current weighting:

        Eligibility = 60%
        Profile Match = 40%

    If profile_match is not available, the eligibility
    score is returned so the ranking system remains
    backward compatible.

    profile_match should contain:

        {
            "match_analysis": {
                "match_score": 0-100
            }
        }
    """

    eligibility_score = calculate_eligibility_score(
        eligibility_result
    )

    # ----------------------------------------
    # No profile match available
    # ----------------------------------------

    if not profile_match:
        return round(eligibility_score, 2)

    match_analysis = profile_match.get(
        "match_analysis",
        {},
    )

    profile_match_score = match_analysis.get(
        "match_score"
    )

    # ----------------------------------------
    # Invalid / missing profile match
    # ----------------------------------------

    if profile_match_score is None:
        return round(eligibility_score, 2)

    try:
        profile_match_score = float(
            profile_match_score
        )
    except (TypeError, ValueError):
        return round(eligibility_score, 2)

    # Keep profile match inside 0-100
    profile_match_score = max(
        0.0,
        min(profile_match_score, 100.0),
    )

    # ----------------------------------------
    # Final weighted score
    # ----------------------------------------

    final_score = (
        eligibility_score * 0.60
        + profile_match_score * 0.40
    )

    return round(final_score, 2)


def determine_risk_level(
    score: float,
    eligibility_result,
) -> str:
    """
    Determine the risk level of a program.

    A mandatory requirement that the student
    does not meet creates High Risk.

    Otherwise:

        75-100 = Low Risk
        50-74  = Medium Risk
        0-49   = High Risk
    """

    for check in eligibility_result.checks:

        status = normalize_status(
            check.status
        )

        # Only a confirmed failure of a mandatory
        # requirement should immediately create
        # high risk.

        if (
            status == "does_not_meet"
            and getattr(check, "mandatory", True)
        ):
            return "High Risk"

    if score >= 75:
        return "Low Risk"

    if score >= 50:
        return "Medium Risk"

    return "High Risk"


def rank_programs(
    profile: StudentProfile,
    programs: list[dict],
) -> list[dict]:
    """
    Compare and rank university programs for a student.

    The function performs:

        1. Eligibility analysis
        2. Profile-to-program matching
        3. Final suitability scoring
        4. Risk determination
        5. Ranking

    Returns programs from highest suitability
    to lowest.
    """

    comparison_results = compare_programs(
        profile=profile,
        programs=programs,
    )

    ranked_programs = []

    for result in comparison_results:

        eligibility = result["eligibility"]

        # ----------------------------------------
        # Profile match
        # ----------------------------------------
        #
        # comparison_service currently returns
        # eligibility only.
        #
        # Therefore profile_match is optional here.
        # The orchestrator can later provide the
        # structured profile match directly.

        profile_match = result.get(
            "profile_match"
        )

        # ----------------------------------------
        # Calculate final score
        # ----------------------------------------

        eligibility_score = (
            calculate_eligibility_score(
                eligibility
            )
        )

        score = calculate_program_score(
            eligibility_result=eligibility,
            profile_match=profile_match,
        )

        risk = determine_risk_level(
            score=score,
            eligibility_result=eligibility,
        )

        ranked_programs.append(
            {
                "university": result["university"],
                "program": result["program"],
                "country": result["country"],
                "degree_level": result["degree_level"],
                "intake": result["intake"],

                # Final suitability score
                "score": score,

                # Keep the individual score visible
                # for debugging and transparency.
                "eligibility_score": (
                    eligibility_score
                ),

                "profile_match_score": (
                    profile_match.get(
                        "match_analysis",
                        {},
                    ).get(
                        "match_score"
                    )
                    if profile_match
                    else None
                ),

                "risk": risk,

                "eligibility_status": (
                    eligibility.overall_status
                ),

                "summary": (
                    eligibility.summary
                ),

                "unknown_requirements": (
                    eligibility.unknown_requirements
                ),
            }
        )

    # ----------------------------------------
    # Highest suitability first
    # ----------------------------------------

    ranked_programs.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    # ----------------------------------------
    # Add ranking position
    # ----------------------------------------

    for position, program in enumerate(
        ranked_programs,
        start=1,
    ):
        program["rank"] = position

    return ranked_programs


if __name__ == "__main__":

    from src.services.program_service import (
        get_available_programs,
    )

    student = StudentProfile(
        name="Abdul Wahab",
        bachelor_degree="BS Computer Science",
        field_of_study="Computer Science",
        university="Islamia University of Bahawalpur",
        cgpa=3.06,
        graduation_year=2026,
        target_degree="Master's",
        target_field=(
            "Computer Science / "
            "Software Engineering"
        ),
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

    programs = get_available_programs()

    ranked = rank_programs(
        profile=student,
        programs=programs,
    )

    print("\nPROGRAM RANKING")
    print("=" * 70)

    for program in ranked:

        print(
            f"\n#{program['rank']} "
            f"{program['university']}"
        )

        print(
            f"Program: "
            f"{program['program']}"
        )

        print(
            f"Final Score: "
            f"{program['score']}/100"
        )

        print(
            f"Eligibility Score: "
            f"{program['eligibility_score']}/100"
        )

        print(
            f"Profile Match Score: "
            f"{program['profile_match_score']}"
        )

        print(
            f"Risk: "
            f"{program['risk']}"
        )

        print(
            f"Eligibility: "
            f"{program['eligibility_status']}"
        )

        print(
            f"Summary: "
            f"{program['summary']}"
        )

    print("\n" + "=" * 70)

