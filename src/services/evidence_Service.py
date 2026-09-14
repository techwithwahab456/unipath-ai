
from src.models.eligibility_result import (
    EligibilityResult,
)


def build_evidence_record(
    requirement: str,
    student_value: str,
    required_value: str,
    status: str,
    explanation: str,
    source: str = "",
    university: str = "",
    program: str = "",
    mandatory: bool = True,
) -> dict:
    """
    Build a structured evidence record for one
    admission requirement.
    """

    return {
        "requirement": requirement,
        "student_value": student_value,
        "required_value": required_value,
        "status": status,
        "explanation": explanation,
        "mandatory": mandatory,
        "source": source,
        "university": university,
        "program": program,
    }


def extract_requirement_evidence(
    eligibility_result: EligibilityResult,
) -> list[dict]:
    """
    Extract evidence records from an EligibilityResult.

    This function preserves the information already
    produced by the eligibility layer.
    """

    evidence = []

    for check in eligibility_result.checks:

        evidence_record = build_evidence_record(
            requirement=check.requirement,
            student_value=check.student_value,
            required_value=check.required_value,
            status=check.status,
            explanation=check.explanation,
            source=check.source,
            university=check.university,
            program=check.program,
            mandatory=check.mandatory,
        )

        evidence.append(
            evidence_record
        )

    return evidence


def classify_evidence_status(
    status: str,
) -> str:
    """
    Convert eligibility status into a simple
    evidence classification.
    """

    normalized = status.lower().strip()

    if normalized == "eligible":
        return "Supporting Evidence"

    if normalized == "partial":
        return "Partial Evidence"

    if normalized == "not_eligible":
        return "Contradicting Evidence"

    if normalized == "unknown":
        return "Insufficient Evidence"

    return "Unclassified"


def enrich_evidence(
    evidence: list[dict],
) -> list[dict]:
    """
    Add an evidence classification to every
    evidence record.
    """

    enriched = []

    for item in evidence:

        enriched_item = item.copy()

        enriched_item["evidence_status"] = (
            classify_evidence_status(
                item.get("status", "")
            )
        )

        enriched.append(
            enriched_item
        )

    return enriched


def get_unknown_evidence(
    eligibility_result: EligibilityResult,
) -> list[str]:
    """
    Return requirements for which the available
    evidence is insufficient.
    """

    unknowns = []

    for check in eligibility_result.checks:

        if (
            check.status.lower().strip()
            == "unknown"
        ):
            unknowns.append(
                check.requirement
            )

    for requirement in (
        eligibility_result.unknown_requirements
    ):

        if requirement not in unknowns:
            unknowns.append(requirement)

    return unknowns


def get_mandatory_gaps(
    eligibility_result: EligibilityResult,
) -> list[dict]:
    """
    Return mandatory requirements that the student
    does not currently satisfy.
    """

    gaps = []

    for check in eligibility_result.checks:

        status = check.status.lower().strip()

        if (
            check.mandatory
            and status == "not_eligible"
        ):

            gaps.append(
                build_evidence_record(
                    requirement=check.requirement,
                    student_value=check.student_value,
                    required_value=check.required_value,
                    status=check.status,
                    explanation=check.explanation,
                    source=check.source,
                    university=check.university,
                    program=check.program,
                    mandatory=check.mandatory,
                )
            )

    return gaps


def build_evidence_summary(
    eligibility_result: EligibilityResult,
) -> dict:
    """
    Build a complete evidence summary for an
    eligibility analysis.
    """

    evidence = extract_requirement_evidence(
        eligibility_result
    )

    evidence = enrich_evidence(
        evidence
    )

    unknowns = get_unknown_evidence(
        eligibility_result
    )

    mandatory_gaps = get_mandatory_gaps(
        eligibility_result
    )

    return {
        "overall_status": (
            eligibility_result.overall_status
        ),
        "evidence": evidence,
        "unknown_requirements": unknowns,
        "mandatory_gaps": mandatory_gaps,
        "evidence_count": len(evidence),
    }


def format_evidence_for_display(
    evidence: list[dict],
) -> str:
    """
    Convert structured evidence into a readable
    text representation.

    Useful for debugging or later API responses.
    """

    lines = []

    for i, item in enumerate(
        evidence,
        start=1,
    ):

        lines.append(
            f"""
Evidence {i}
Requirement: {item['requirement']}
Student Value: {item['student_value']}
Required Value: {item['required_value']}
Status: {item['status']}
Evidence Status: {item['evidence_status']}
Mandatory: {item['mandatory']}
University: {item['university']}
Program: {item['program']}
Source: {item['source']}
Explanation: {item['explanation']}
"""
        )

    return "\n".join(lines)


if __name__ == "__main__":

    eligibility = EligibilityResult(
        overall_status="Partially Eligible",

        checks=[],

        unknown_requirements=[
            "Minimum CGPA"
        ],

        application_documents=[
            "Passport",
            "CV",
            "Transcript",
        ],

        summary=(
            "Some requirements could not "
            "be confirmed."
        ),
    )

    result = build_evidence_summary(
        eligibility
    )

    print("\nEVIDENCE SUMMARY")
    print("=" * 60)

    print(
        f"Overall status: "
        f"{result['overall_status']}"
    )

    print(
        f"Evidence count: "
        f"{result['evidence_count']}"
    )

    print("\nUnknown Requirements:")

    for item in result[
        "unknown_requirements"
    ]:
        print(f"- {item}")

    print("\nMandatory Gaps:")

    for item in result[
        "mandatory_gaps"
    ]:
        print(
            f"- {item['requirement']}"
        )

    print("=" * 60)

