from dataclasses import dataclass, field


@dataclass
class RequirementCheck:

    requirement: str
    student_value: str
    required_value: str
    status: str
    explanation: str


@dataclass
class EligibilityResult:

    overall_status: str

    checks: list[RequirementCheck] = field(
        default_factory=list
    )

    unknown_requirements: list[str] = field(
        default_factory=list
    )

    application_documents: list[str] = field(
        default_factory=list
    )

    summary: str = ""