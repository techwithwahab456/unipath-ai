import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.models.eligibility_result import (
    EligibilityResult,
    RequirementCheck,
)
from src.models.student_profile import StudentProfile
from src.rag.retriever import retrieve_documents


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


RELEVANCE_THRESHOLD = 1.25


def analyze_eligibility(
    profile: StudentProfile,
    filters: dict | None = None,
    n_results: int = 8,
) -> EligibilityResult:

    # --------------------------------------------------
    # 1. Requirement-focused retrieval queries
    # --------------------------------------------------

    queries = [

        f"""
What bachelor's degree and field of study are required
for the {profile.target_degree} in {profile.target_field}?
""",

        f"""
What is the minimum CGPA required for admission to
the {profile.target_degree} in {profile.target_field}?
""",

        f"""
What English language or IELTS score is required for
the {profile.target_degree} in {profile.target_field}?
""",

        f"""
What application documents are required for admission
to the {profile.target_degree} in {profile.target_field}?
""",
    ]


    all_documents = []
    all_metadatas = []
    all_distances = []


    # --------------------------------------------------
    # 2. Retrieve evidence for each requirement
    # --------------------------------------------------

    for query in queries:

        results = retrieve_documents(
            question=query,
            filters=filters,
            n_results=n_results,
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]


        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            if distance <= RELEVANCE_THRESHOLD:

                all_documents.append(document)
                all_metadatas.append(metadata)
                all_distances.append(distance)


    # --------------------------------------------------
    # 3. Remove duplicate chunks
    # --------------------------------------------------

    unique_documents = []
    unique_metadatas = []

    seen_documents = set()


    for document, metadata in zip(
        all_documents,
        all_metadatas,
    ):

        if document not in seen_documents:

            seen_documents.add(document)

            unique_documents.append(document)
            unique_metadatas.append(metadata)


    # --------------------------------------------------
    # 4. No relevant evidence
    # --------------------------------------------------

    if not unique_documents:

        return EligibilityResult(
            overall_status="Insufficient Information",
            summary=(
                "No sufficiently relevant university "
                "admission requirements were found."
            ),
        )


    # --------------------------------------------------
    # 5. Build university context
    # --------------------------------------------------

    context = "\n\n".join(
        unique_documents
    )


    # --------------------------------------------------
    # 6. Ask Gemini for structured comparison
    # --------------------------------------------------

    prompt = f"""
You are UniPath AI, an evidence-based university
admission eligibility analyzer.

Compare the student's profile against ONLY the
university information provided in the context.

Do NOT use outside knowledge.

STUDENT PROFILE

Name:
{profile.name}

Bachelor Degree:
{profile.bachelor_degree}

Field of Study:
{profile.field_of_study}

University:
{profile.university}

CGPA:
{profile.cgpa}

Graduation Year:
{profile.graduation_year}

Target Degree:
{profile.target_degree}

Target Field:
{profile.target_field}

English Test:
{profile.english_test}

English Score:
{profile.english_score}

Skills:
{profile.skills}

Projects:
{profile.projects}

Work Experience:
{profile.work_experience}


UNIVERSITY DOCUMENT EVIDENCE

{context}


YOUR TASK

Evaluate only requirements explicitly supported
by the university evidence.

For every evaluated requirement return:

- requirement
- student_value
- required_value
- status
- explanation

Allowed status values:

- Meets
- Does Not Meet
- Likely Meets
- Unknown


IMPORTANT:

If the university document does not contain a
requirement, do NOT invent one.

If there is insufficient information to evaluate
something, put it inside unknown_requirements.

Application documents such as:

- transcript
- CV
- motivation letter
- passport
- recommendation letter

must NOT be placed inside unknown_requirements.

Instead, put them inside application_documents
if the university document explicitly mentions them.


OVERALL STATUS

Use:

"Likely Eligible"

when all evaluated mandatory requirements
are satisfied and no evaluated requirement
is failed.

Use:

"Not Eligible"

when at least one explicitly evaluated
mandatory requirement is not satisfied.

Use:

"Needs Review"

when important requirements cannot
be determined from the available evidence.

Use:

"Insufficient Information"

when there is not enough university evidence
to perform a meaningful evaluation.


Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_status": "...",

    "checks": [
        {{
            "requirement": "...",
            "student_value": "...",
            "required_value": "...",
            "status": "...",
            "explanation": "..."
        }}
    ],

    "unknown_requirements": [],

    "application_documents": [],

    "summary": "..."
}}
"""


    # --------------------------------------------------
    # 7. Call Gemini
    # --------------------------------------------------

    response = llm.invoke(prompt)

    content = response.content


    # --------------------------------------------------
    # 8. Extract response text
    # --------------------------------------------------

    if isinstance(content, list):

        answer = ""

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):

                answer += item.get(
                    "text",
                    "",
                )

    else:

        answer = str(content)


    # --------------------------------------------------
    # 9. Clean JSON markdown
    # --------------------------------------------------

    answer = answer.strip()


    if answer.startswith("```json"):

        answer = answer[7:]


    elif answer.startswith("```"):

        answer = answer[3:]


    if answer.endswith("```"):

        answer = answer[:-3]


    answer = answer.strip()


    # --------------------------------------------------
    # 10. Parse JSON
    # --------------------------------------------------

    try:

        data = json.loads(answer)

    except json.JSONDecodeError:

        return EligibilityResult(
            overall_status="Analysis Error",
            summary=(
                "The AI returned an invalid structured "
                "eligibility result."
            ),
        )


    # --------------------------------------------------
    # 11. Build RequirementCheck objects
    # --------------------------------------------------

    checks = []


    for item in data.get(
        "checks",
        [],
    ):

        checks.append(
            RequirementCheck(

                requirement=item.get(
                    "requirement",
                    "Unknown",
                ),

                student_value=item.get(
                    "student_value",
                    "Unknown",
                ),

                required_value=item.get(
                    "required_value",
                    "Unknown",
                ),

                status=item.get(
                    "status",
                    "Unknown",
                ),

                explanation=item.get(
                    "explanation",
                    "",
                ),
            )
        )


    # --------------------------------------------------
    # 12. Return structured result
    # --------------------------------------------------

    return EligibilityResult(

        overall_status=data.get(
            "overall_status",
            "Needs Review",
        ),

        checks=checks,

        unknown_requirements=data.get(
            "unknown_requirements",
            [],
        ),

        application_documents=data.get(
            "application_documents",
            [],
        ),

        summary=data.get(
            "summary",
            "",
        ),
    )