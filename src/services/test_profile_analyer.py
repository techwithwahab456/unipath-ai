from src.models.student_profile import StudentProfile
from src.services.profile_analyzer import analyze_student_profile


profile = StudentProfile(

    name="Abdul Wahab",

    bachelor_degree="BS Computer Science",

    field_of_study="Computer Science",

    university="Your University Name",

    cgpa=3.1,

    graduation_year=2026,

    target_degree="Master's",

    target_field="Artificial Intelligence and Machine Learning",

    target_countries=[
        "France",
        "Germany"
    ],

    skills=[
        "Flutter",
        "Firebase",
        "Python",
        "REST APIs",
        "Django REST Framework",
        "RAG",
        "ChromaDB",
        "LangChain"
    ],

    projects=[
        "Flutter E-commerce Application",
        "RAG Document Question Answering System",
        "Student Score Prediction using Linear Regression"
    ],

    work_experience=[
        "Flutter Developer Experience"
    ],

    english_test="IELTS",

    english_score=None
)


result = analyze_student_profile(profile)

print("\n" + "=" * 60)
print("STUDENT PROFILE ANALYSIS")
print("=" * 60 + "\n")

print(result)