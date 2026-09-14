
from src.models.student_profile import StudentProfile
from src.models.eligibility_result import EligibilityResult


def normalize_document_name(document: str) -> str:
    """
    Normalize an application document name so that
    similar document names are easier to compare.
    """

    return document.strip().lower()


def build_document_checklist(
    profile: StudentProfile,
    eligibility_result: EligibilityResult,
) -> list[dict]:
    """
    Build a student-specific application document checklist.

    Only documents found in the EligibilityResult are included.
    This service does not invent university requirements.
    """

    documents = eligibility_result.application_documents

    checklist = []

    seen = set()

    for document in documents:

        if not document:
            continue

        normalized = normalize_document_name(
            document
        )

        if normalized in seen:
            continue

        seen.add(normalized)

        checklist.append(
            {
                "document": document.strip(),
                "status": "Required",
                "student_provided": False,
                "notes": "",
            }
        )

    return checklist


def get_missing_documents(
    checklist: list[dict],
) -> list[str]:
    """
    Return documents that have not yet been provided.
    """

    return [
        item["document"]
        for item in checklist
        if not item["student_provided"]
    ]


def mark_document_provided(
    checklist: list[dict],
    document_name: str,
) -> list[dict]:
    """
    Mark a document as provided by the student.
    """

    target = normalize_document_name(
        document_name
    )

    updated_checklist = []

    for item in checklist:

        current = normalize_document_name(
            item["document"]
        )

        updated_item = item.copy()

        if current == target:

            updated_item["student_provided"] = True
            updated_item["status"] = "Provided"

        updated_checklist.append(updated_item)

    return updated_checklist


def get_document_progress(
    checklist: list[dict],
) -> dict:
    """
    Calculate application-document completion progress.
    """

    total = len(checklist)

    provided = sum(
        1
        for item in checklist
        if item["student_provided"]
    )

    missing = total - provided

    percentage = (
        (provided / total) * 100
        if total > 0
        else 0
    )

    return {
        "total_documents": total,
        "provided_documents": provided,
        "missing_documents": missing,
        "completion_percentage": round(
            percentage,
            2,
        ),
    }


def build_application_document_result(
    profile: StudentProfile,
    eligibility_result: EligibilityResult,
) -> dict:
    """
    Build the complete application-document analysis.
    """

    checklist = build_document_checklist(
        profile=profile,
        eligibility_result=eligibility_result,
    )

    missing_documents = get_missing_documents(
        checklist
    )

    progress = get_document_progress(
        checklist
    )

    return {
        "student": profile.name,
        "checklist": checklist,
        "missing_documents": missing_documents,
        "progress": progress,
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
            "from available university evidence."
        ),
    )

    result = build_application_document_result(
        profile=student,
        eligibility_result=eligibility,
    )

    print("\nAPPLICATION DOCUMENT CHECKLIST")
    print("=" * 60)

    for item in result["checklist"]:

        print(
            f"[{item['status']}] "
            f"{item['document']}"
        )

    print("\nMISSING DOCUMENTS:")

    for document in result["missing_documents"]:
        print(f"- {document}")

    print("\nPROGRESS:")
    print(result["progress"])

    print("=" * 60)

