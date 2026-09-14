
from src.models.student_profile import StudentProfile

from src.services.program_services import (
    get_available_programs,
)

from src.services.program_filter_services import (
    filter_programs_for_student,
)

from src.services.eligibility_services import (
    analyze_eligibility,
)

from src.services.evidence_Service import (
    build_evidence_summary,
)

from src.services.profile_matching_service import (
    match_profile_to_program,
)

from src.services.ranking_service import (
    calculate_eligibility_score,
    calculate_program_score,
    determine_risk_level,
)

from src.services.recomendation_services import (
    classify_program,
    build_recommendation_reason,
)

from src.services.application_document_Services import (
    build_document_checklist,
)

from src.services.application_checklist_services import (
    build_application_checklist,
)

from src.services.admission_strategy_services import (
    build_admission_strategy,
)


def analyze_single_program(
    profile: StudentProfile,
    program: dict,
    available_documents: list[str] | None = None,
) -> dict:
    """
    Analyze one university program through all
    program-level UniPath AI layers.

    Flow:

        Program
           ↓
        Eligibility
           ↓
        Evidence
           ↓
        Profile Matching
           ↓
        Final Ranking Score
           ↓
        Risk
           ↓
        Recommendation
           ↓
        Application Documents
           ↓
        Application Checklist
    """

    university = program.get(
        "university",
        "Unknown",
    )

    program_name = program.get(
        "program",
        "Unknown",
    )

    filters = {
        "university": university,
        "program": program_name,
    }

    # =================================================
    # 1. ELIGIBILITY
    # =================================================

    eligibility = analyze_eligibility(
        profile=profile,
        filters=filters,
        n_results=8,
    )

    # =================================================
    # 2. EVIDENCE
    # =================================================

    evidence = build_evidence_summary(
        eligibility_result=eligibility,
    )

    # =================================================
    # 3. PROFILE MATCHING
    # =================================================

    profile_match = match_profile_to_program(
        profile=profile,
        program=program,
        eligibility_result=eligibility,
    )

    # =================================================
    # 4. INDIVIDUAL SCORES
    # =================================================

    eligibility_score = calculate_eligibility_score(
        eligibility_result=eligibility,
    )

    # =================================================
    # 5. FINAL PROGRAM SCORE
    # =================================================
    #
    # New ranking system:
    #
    # Eligibility   = 60%
    # Profile Match = 40%
    #
    # The profile_match object contains:
    #
    # profile_match["match_analysis"]["match_score"]
    #

    score = calculate_program_score(
        eligibility_result=eligibility,
        profile_match=profile_match,
    )

    # =================================================
    # 6. RISK
    # =================================================

    risk = determine_risk_level(
        score=score,
        eligibility_result=eligibility,
    )

    # =================================================
    # 7. RECOMMENDATION CATEGORY
    # =================================================

    category = classify_program(
        score=score,
    )

    recommendation = build_recommendation_reason(
        {
            "score": score,
            "risk": risk,
            "eligibility_status": (
                eligibility.overall_status
            ),
            "category": category,
        }
    )

    # =================================================
    # 8. APPLICATION DOCUMENT REQUIREMENTS
    # =================================================

    document_requirements = (
        build_document_checklist(
            profile=profile,
            eligibility_result=eligibility,
        )
    )

    # =================================================
    # 9. APPLICATION CHECKLIST
    # =================================================

    application_checklist = (
        build_application_checklist(
            profile=profile,
            eligibility_result=eligibility,
            available_documents=available_documents,
        )
    )

    # =================================================
    # 10. PROFILE MATCH SCORE
    # =================================================

    match_analysis = profile_match.get(
        "match_analysis",
        {},
    )

    profile_match_score = match_analysis.get(
        "match_score"
    )

    # =================================================
    # 11. COMPLETE PROGRAM RESULT
    # =================================================

    return {
        "university": university,

        "program": program_name,

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

        # -----------------------------
        # Ranking
        # -----------------------------

        "score": score,

        "eligibility_score": (
            eligibility_score
        ),

        "profile_match_score": (
            profile_match_score
        ),

        "risk": risk,

        "category": category,

        # -----------------------------
        # Analysis
        # -----------------------------

        "recommendation": recommendation,

        "eligibility": eligibility,

        "evidence": evidence,

        "profile_match": profile_match,

        # -----------------------------
        # Application preparation
        # -----------------------------

        "document_requirements": (
            document_requirements
        ),

        "application_checklist": (
            application_checklist
        ),
    }


def run_admission_orchestrator(
    profile: StudentProfile,
    programs: list[dict] | None = None,
    available_documents: list[str] | None = None,
) -> dict:
    """
    Run the complete UniPath AI admission architecture.

    High-level flow:

        Student Profile
              ↓
        Program Discovery
              ↓
        Program Filtering
              ↓
        Program Analysis
              ↓
        Eligibility
              +
        Profile Matching
              ↓
        Final Scoring
              ↓
        Ranking
              ↓
        Admission Strategy
              ↓
        Final Result
    """

    # =================================================
    # STEP 1 — PROGRAM DISCOVERY
    # =================================================

    if programs is None:

        all_programs = get_available_programs()

    else:

        all_programs = programs

    # =================================================
    # STEP 2 — PROGRAM FILTERING
    # =================================================

    filtered_programs = (
        filter_programs_for_student(
            profile=profile,
            programs=all_programs,
        )
    )

    # =================================================
    # STEP 3 — ANALYZE EACH PROGRAM
    # =================================================

    program_results = []

    for program in filtered_programs:

        result = analyze_single_program(
            profile=profile,
            program=program,
            available_documents=available_documents,
        )

        program_results.append(result)

    # =================================================
    # STEP 4 — RANK PROGRAMS
    # =================================================

    # Highest final suitability score first.

    program_results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    # Add final ranking position.

    for rank, result in enumerate(
        program_results,
        start=1,
    ):

        result["rank"] = rank

    # =================================================
    # STEP 5 — ADMISSION STRATEGY
    # =================================================

    strategy = build_admission_strategy(
        programs=program_results,
        priority_limit=3,
    )

    # =================================================
    # STEP 6 — FINAL SYSTEM RESULT
    # =================================================

    return {
        "student": profile.model_dump(),

        "program_discovery": {
            "total_programs": len(
                all_programs
            ),
        },

        "program_filtering": {
            "programs_before_filter": len(
                all_programs
            ),

            "programs_after_filter": len(
                filtered_programs
            ),
        },

        "programs": program_results,

        "admission_strategy": strategy,
    }


if __name__ == "__main__":

    student = StudentProfile(
        name="Abdul Wahab",

        bachelor_degree=(
            "BS Computer Science"
        ),

        field_of_study=(
            "Computer Science"
        ),

        university=(
            "Islamia University of Bahawalpur"
        ),

        cgpa=3.06,

        graduation_year=2026,

        target_degree="Master's",

        target_field=(
            "Computer Science / "
            "Software Engineering"
        ),

        target_countries=[
            "France"
        ],

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

    # Only documents explicitly supplied
    # by the student should be marked
    # as available.

    available_documents = [
        "Passport",
        "CV",
        "Academic Transcript",
    ]

    print("\n")
    print("=" * 70)
    print(
        "UNIPATH AI — ADMISSION ORCHESTRATOR"
    )
    print("=" * 70)

    # =================================================
    # RUN SYSTEM
    # =================================================

    result = run_admission_orchestrator(
        profile=student,
        available_documents=available_documents,
    )

    # =================================================
    # PROGRAM FILTERING
    # =================================================

    print("\nPROGRAM FILTERING")
    print("-" * 70)

    print(
        "Programs before filtering:",
        result[
            "program_filtering"
        ][
            "programs_before_filter"
        ],
    )

    print(
        "Programs after filtering:",
        result[
            "program_filtering"
        ][
            "programs_after_filter"
        ],
    )

    # =================================================
    # RANKED PROGRAMS
    # =================================================

    print("\nRANKED PROGRAMS")
    print("-" * 70)

    for program in result["programs"]:

        print(
            f"\n{program['rank']}. "
            f"{program['university']}"
        )

        print(
            f"   Program: "
            f"{program['program']}"
        )

        print(
            f"   Final Score: "
            f"{program['score']}/100"
        )

        print(
            f"   Eligibility Score: "
            f"{program['eligibility_score']}/100"
        )

        print(
            f"   Profile Match Score: "
            f"{program['profile_match_score']}"
        )

        print(
            f"   Risk: "
            f"{program['risk']}"
        )

        print(
            f"   Category: "
            f"{program['category']}"
        )

        print(
            f"   Eligibility: "
            f"{program['eligibility'].overall_status}"
        )

        print(
            f"   Recommendation: "
            f"{program['recommendation']}"
        )

    # =================================================
    # ADMISSION STRATEGY
    # =================================================

    print("\nADMISSION STRATEGY")
    print("-" * 70)

    strategy = result[
        "admission_strategy"
    ]

    print(
        "Strategy:",
        strategy["strategy"],
    )

    print(
        "Category counts:",
        strategy["category_counts"],
    )

    print(
        "Category percentages:",
        strategy["category_percentages"],
    )

    print("\nPriority Programs:")

    for program in strategy[
        "priority_programs"
    ]:

        print(
            f"{program['rank']}. "
            f"{program['university']} | "
            f"{program['program']} | "
            f"{program['category']}"
        )

    print("\n")
    print("=" * 70)
    print(
        "ORCHESTRATION COMPLETE"
    )
    print("=" * 70)

