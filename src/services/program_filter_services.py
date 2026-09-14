
from src.models.student_profile import StudentProfile
from src.services.program_services import get_available_programs


def normalize_degree_level(degree_level: str) -> str:
    """
    Normalize different ways of writing master's degree levels.

    Examples:
        Master's -> master
        Master -> master
        Master 1 -> master
        Master 2 -> master
    """

    if not degree_level:
        return ""

    value = degree_level.strip().lower()

    if value in {
        "master",
        "master's",
        "masters",
        "master 1",
        "master 2",
        "m1",
        "m2",
    }:
        return "master"

    if value in {
        "bachelor",
        "bachelor's",
        "bachelors",
        "licence",
        "undergraduate",
    }:
        return "bachelor"

    if value in {
        "phd",
        "doctorate",
        "doctoral",
    }:
        return "phd"

    return value


def filter_by_country(
    programs: list[dict],
    countries: list[str],
) -> list[dict]:
    """
    Keep programs whose country matches one of
    the student's target countries.
    """

    if not countries:
        return programs

    target_countries = {
        country.strip().lower()
        for country in countries
    }

    return [
        program
        for program in programs
        if program.get("country", "").strip().lower()
        in target_countries
    ]


def filter_by_degree_level(
    programs: list[dict],
    degree_level: str,
) -> list[dict]:
    """
    Keep programs matching the requested academic level.

    Degree levels are normalized before comparison.

    Example:

        Student: Master's
        Program: Master 1       -> MATCH
        Program: Master 2       -> MATCH
        Program: Master         -> MATCH
    """

    if not degree_level:
        return programs

    target = normalize_degree_level(degree_level)

    return [
        program
        for program in programs
        if normalize_degree_level(
            program.get("degree_level", "")
        ) == target
    ]


def filter_by_intake(
    programs: list[dict],
    intake: str,
) -> list[dict]:
    """
    Keep programs matching the requested intake.

    This is an explicit filter. It is NOT automatically
    applied from StudentProfile because document intake
    and student's target intake can represent different
    things.
    """

    if not intake:
        return programs

    target = intake.strip().lower()

    return [
        program
        for program in programs
        if program.get(
            "intake",
            "",
        ).strip().lower() == target
    ]


def filter_by_program_keyword(
    programs: list[dict],
    keyword: str,
) -> list[dict]:
    """
    Keep programs whose program name contains
    the requested keyword.

    This remains a literal keyword filter and should
    only be used when the user explicitly provides
    a program-name keyword.
    """

    if not keyword:
        return programs

    keyword = keyword.strip().lower()

    return [
        program
        for program in programs
        if keyword in program.get(
            "program",
            "",
        ).strip().lower()
    ]


def filter_programs(
    programs: list[dict],
    countries: list[str] | None = None,
    degree_level: str | None = None,
    intake: str | None = None,
    program_keyword: str | None = None,
) -> list[dict]:
    """
    Apply explicit program filters.

    Filters are applied progressively:

        All Programs
             ↓
        Country
             ↓
        Degree Level
             ↓
        Intake
             ↓
        Program Keyword
    """

    filtered = programs

    if countries:
        filtered = filter_by_country(
            programs=filtered,
            countries=countries,
        )

    if degree_level:
        filtered = filter_by_degree_level(
            programs=filtered,
            degree_level=degree_level,
        )

    if intake:
        filtered = filter_by_intake(
            programs=filtered,
            intake=intake,
        )

    if program_keyword:
        filtered = filter_by_program_keyword(
            programs=filtered,
            keyword=program_keyword,
        )

    return filtered


def filter_programs_for_student(
    profile: StudentProfile,
    programs: list[dict] | None = None,
    degree_level: str | None = None,
    intake: str | None = None,
    program_keyword: str | None = None,
) -> list[dict]:
    """
    Filter available programs according to the student's
    explicit profile preferences.

    Automatically applies:

        target_countries
        target_degree

    It does NOT automatically use target_field as a literal
    program-name keyword.

    Academic field compatibility is handled later by the
    eligibility and profile-matching layers.
    """

    if programs is None:
        programs = get_available_programs()

    return filter_programs(
        programs=programs,
        countries=profile.target_countries,
        degree_level=degree_level
        or profile.target_degree,
        intake=intake,
        program_keyword=program_keyword,
    )


def summarize_filter_result(
    original_programs: list[dict],
    filtered_programs: list[dict],
) -> dict:
    """
    Return a simple summary of the filtering operation.
    """

    original_count = len(original_programs)
    filtered_count = len(filtered_programs)

    return {
        "original_count": original_count,
        "filtered_count": filtered_count,
        "removed_count": (
            original_count - filtered_count
        ),
    }


if __name__ == "__main__":

    student = StudentProfile(
        name="Abdul Wahab",
        bachelor_degree="BS Computer Science",
        field_of_study="Computer Science",
        university="Islamia University of Bahawalpur",
        cgpa=3.06,
        graduation_year=2026,
        target_degree="Master's",
        target_field="Computer Science",
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

    filtered_programs = filter_programs_for_student(
        profile=student,
        programs=programs,
    )

    summary = summarize_filter_result(
        original_programs=programs,
        filtered_programs=filtered_programs,
    )

    print("\nPROGRAM FILTER RESULT")
    print("=" * 60)

    print(
        f"Original programs: "
        f"{summary['original_count']}"
    )

    print(
        f"Filtered programs: "
        f"{summary['filtered_count']}"
    )

    print(
        f"Removed programs: "
        f"{summary['removed_count']}"
    )

    print("\nMATCHING PROGRAMS:")
    print("-" * 60)

    for i, program in enumerate(
        filtered_programs,
        start=1,
    ):

        print(
            f"{i}. "
            f"{program['university']} | "
            f"{program['program']} | "
            f"{program['degree_level']} | "
            f"{program['intake']}"
        )

    print("=" * 60)

