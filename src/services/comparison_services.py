from src.models.eligibility_result import EligibilityResult
from src.models.student_profile import StudentProfile
from src.services.eligibility_services import analyze_eligibility


def compare_programs(
    profile: StudentProfile,
    programs: list[dict],
) -> list[dict]:
    """
    Compare a student's eligibility across multiple
    university programs.

    Each program dictionary should contain metadata such as:

    {
        "university": "...",
        "program": "...",
        "country": "...",
        "degree_level": "...",
        "intake": "..."
    }

    Returns a list containing the eligibility result
    for every program.
    """

    comparison_results = []

    # --------------------------------------------------
    # 1. Analyze every program
    # --------------------------------------------------

    for program in programs:

        filters = {
            "university": program["university"],
            "program": program["program"],
        }

        eligibility = analyze_eligibility(
            profile=profile,
            filters=filters,
            n_results=8,
        )

        # --------------------------------------------------
        # 2. Store program + eligibility information
        # --------------------------------------------------

        comparison_results.append(
            {
                "university": program["university"],
                "program": program["program"],
                "country": program.get(
                    "country",
                    "Unknown",
                ),
                "degree_level": program.get(
                    "degree_level",
                    "Unknown",
                ),
                "intake": program.get(
                    "intake",
                    "Unknown",
                ),
                "eligibility": eligibility,
            }
        )

    return comparison_results