from src.models.student_profile import StudentProfile
from src.services.eligibility_services import analyze_eligibility


student = StudentProfile(
    name="Test Student",

    bachelor_degree="Bachelor's in Computer Science",

    field_of_study="Computer Science",

    university="Test University",

    cgpa=3.1,

    graduation_year=2026,

    target_degree="Master's",

    target_field="Artificial Intelligence",

    target_countries=["France"],

    skills=[
        "Flutter",
        "Python",
        "Machine Learning",
    ],

    projects=[
        "RAG University Admission Assistant",
    ],

    work_experience=[],

    english_test="IELTS",

    english_score=6.5,
)


result = analyze_eligibility(
    profile=student,
)


print("\n==============================")
print("ELIGIBILITY ANALYSIS")
print("==============================")


print("\nOVERALL STATUS")
print("------------------------------")
print(result.overall_status)


print("\nSUMMARY")
print("------------------------------")
print(result.summary)


print("\nREQUIREMENT CHECKS")
print("------------------------------")

for check in result.checks:

    print(f"\nRequirement: {check.requirement}")

    print(
        f"Student Value: "
        f"{check.student_value}"
    )

    print(
        f"Required Value: "
        f"{check.required_value}"
    )

    print(
        f"Status: "
        f"{check.status}"
    )

    print(
        f"Explanation: "
        f"{check.explanation}"
    )


print("\nUNKNOWN REQUIREMENTS")
print("------------------------------")

if result.unknown_requirements:

    for item in result.unknown_requirements:

        print(f"- {item}")

else:

    print("None")


print("\nAPPLICATION DOCUMENTS")
print("------------------------------")

if result.application_documents:

    for item in result.application_documents:

        print(f"- {item}")

else:

    print("None") 