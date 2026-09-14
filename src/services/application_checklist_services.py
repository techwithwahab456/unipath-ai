
from src.models.student_profile import StudentProfile
from src.services.application_document_Services import (
    build_document_checklist,
    get_document_progress,
)


def build_student_document_checklist(
    profile: StudentProfile,
    eligibility_result,
    available_documents: list[str] | None = None,
) -> list[dict]:
    """
    Build an application checklist and mark documents
    that the student has already provided.

    Important:
    The university-required documents come only from
    the eligibility result.

    The available_documents list represents documents
    explicitly provided by the student.
    """

    if available_documents is None:
        available_documents = []

    required_checklist = build_document_checklist(
        profile=profile,
        eligibility_result=eligibility_result,
    )

    available_normalized = {
        document.strip().lower()
        for document in available_documents
        if document
    }

    checklist = []

    for item in required_checklist:

        updated_item = item.copy()

        document_name = (
            item["document"]
            .strip()
            .lower()
        )

        if document_name in available_normalized:

            updated_item["student_provided"] = True
            updated_item["status"] = "Provided"

        else:

            updated_item["student_provided"] = False
            updated_item["status"] = "Missing"

        checklist.append(updated_item)

    return checklist


def get_missing_application_documents(
    checklist: list[dict],
) -> list[str]:
    """
    Return all required documents that are still missing.
    """

    return [
        item["document"]
        for item in checklist
        if not item["student_provided"]
    ]


def get_provided_application_documents(
    checklist: list[dict],
) -> list[str]:
    """
    Return all required documents already provided.
    """

    return [
        item["document"]
        for item in checklist
        if item["student_provided"]
    ]


def calculate_checklist_progress(
    checklist: list[dict],
) -> dict:
    """
    Calculate application-document completion.
    """

    progress = get_document_progress(
        checklist
    )

    return progress


def build_application_checklist(
    profile: StudentProfile,
    eligibility_result,
    available_documents: list[str] | None = None,
) -> dict:
    """
    Build the complete application checklist.

    Returns:

        student
        checklist
        provided_documents
        missing_documents
        progress
    """

    checklist = build_student_document_checklist(
        profile=profile,
        eligibility_result=eligibility_result,
        available_documents=available_documents,
    )

    provided_documents = (
        get_provided_application_documents(
            checklist
        )
    )

    missing_documents = (
        get_missing_application_documents(
            checklist
        )
    )

    progress = calculate_checklist_progress(
        checklist
    )

    return {
        "student": profile.name,
        "checklist": checklist,
        "provided_documents": provided_documents,
        "missing_documents": missing_documents,
        "progress": progress,
    }


def print_application_checklist(
    result: dict,
) -> None:
    """
    Print the checklist in a readable format.
    """

    print("\nAPPLICATION CHECKLIST")
    print("=" * 60)

    for item in result["checklist"]:

        status = item["status"]

        print(
            f"[{status}] "
            f"{item['document']}"
        )

    print("\nPROVIDED:")
    print("-" * 60)

    for document in result[
        "provided_documents"
    ]:
        print(f"- {document}")

    print("\nMISSING:")
    print("-" * 60)

    for document in result[
        "missing_documents"
    ]:
        print(f"- {document}")

    print("\nPROGRESS:")
    print("-" * 60)

    progress = result["progress"]

    print(
        f"{progress['provided_documents']} / "
        f"{progress['total_documents']} documents"
    )

    print(
        f"Completion: "
        f"{progress['completion_percentage']}%"
    )

    print("=" * 60)


if __name__ == "__main__":

    from src.models.eligibility_result import (
        EligibilityResult,
    )

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

    eligibility = EligibilityResult(
        overall_status="Partially Eligible",

        application_documents=[
            "Passport",
            "CV",
            "Motivation Letter",
            "Academic Transcript",
            "Recommendation Letter",
            "English Certificate",
        ],

        summary=(
            "Application documents identified "
            "from university evidence."
        ),
    )

    # These represent documents explicitly
    # provided by the student.
    available_documents = [
        "Passport",
        "CV",
        "Academic Transcript",
    ]

    result = build_application_checklist(
        profile=student,
        eligibility_result=eligibility,
        available_documents=available_documents,
    )

    print_application_checklist(
        result
    )

