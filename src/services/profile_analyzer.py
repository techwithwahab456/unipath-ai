from src.config.llm import llm
from src.models.student_profile import StudentProfile


def analyze_student_profile(profile: StudentProfile):

    prompt = f"""
You are an AI university admission profile analyst.

Analyze this student's profile for admission to a Master's degree.

Student Profile:

Name: {profile.name}

Bachelor Degree: {profile.bachelor_degree}

Field of Study: {profile.field_of_study}

University: {profile.university}

CGPA: {profile.cgpa}

Graduation Year: {profile.graduation_year}

Target Degree: {profile.target_degree}

Target Field: {profile.target_field}

Target Countries: {", ".join(profile.target_countries)}

Technical Skills:
{", ".join(profile.skills)}

Projects:
{", ".join(profile.projects)}

Work Experience:
{", ".join(profile.work_experience)}

English Test:
{profile.english_test or "Not provided"}

English Score:
{profile.english_score or "Not provided"}


Analyze the profile and provide:

1. PROFILE SUMMARY
2. STRONGEST POINTS
3. WEAKNESSES OR RISKS
4. ADMISSION READINESS
5. SKILLS GAPS FOR THE TARGET FIELD
6. PROJECT GAPS
7. WHAT THE STUDENT SHOULD IMPROVE
8. RECOMMENDED UNIVERSITY COMPETITIVENESS LEVEL:
   - Ambitious
   - Realistic
   - Safe

Be honest and critical.

Do not invent achievements or qualifications.

Clearly distinguish facts from recommendations.
"""

    response = llm.invoke(prompt)

    return response.content