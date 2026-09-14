
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


# Temporary retrieval threshold.
# We will retune this after the final 600/100
# document rebuild.
RELEVANCE_THRESHOLD = 1.25


def extract_llm_text(response) -> str:
    """
    Extract text from the Gemini response.
    """

    content = response.content

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

        return answer.strip()

    return str(content).strip()


def clean_json_response(
    text: str,
) -> str:
    """
    Remove markdown code fences if Gemini returns
    JSON inside ```json ... ```.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def normalize_status(
    status: str,
) -> str:
    """
    Normalize the status returned by the LLM.
    """

    normalized = (
        status
        .strip()
        .lower()
    )

    mapping = {
        "meets": "Meets",
        "does not meet": "Does Not Meet",
        "likely meets": "Likely Meets",
        "unknown": "Unknown",
    }

    return mapping.get(
        normalized,
        "Unknown",
    )


def normalize_boolean(
    value,
) -> bool:
    """
    Safely convert an LLM value into a boolean.
    """

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        return (
            value.strip().lower()
            in {
                "true",
                "yes",
                "mandatory",
                "required",
            }
        )

    return bool(value)


def build_evidence_metadata(
    metadatas: list[dict],
) -> list[dict]:
    """
    Build a compact list of valid evidence metadata.

    Gemini will be instructed to use only these
    sources when returning source information.
    """

    evidence_metadata = []

    seen = set()

    for metadata in metadatas:

        source = metadata.get(
            "source",
            "Unknown",
        )

        university = metadata.get(
            "university",
            "Unknown",
        )

        program = metadata.get(
            "program",
            "Unknown",
        )

        chunk_index = metadata.get(
            "chunk_index",
            "Unknown",
        )

        key = (
            source,
            chunk_index,
        )

        if key in seen:
            continue

        seen.add(key)

        evidence_metadata.append(
            {
                "source": source,
                "university": university,
                "program": program,
                "chunk_index": chunk_index,
            }
        )

    return evidence_metadata


def find_source_metadata(
    source: str,
    metadatas: list[dict],
) -> dict:
    """
    Find the actual retrieved metadata corresponding
    to a source returned by Gemini.

    If Gemini returns an invalid source, return
    safe Unknown values.
    """

    normalized_source = (
        source.strip().lower()
        if source
        else ""
    )

    for metadata in metadatas:

        actual_source = str(
            metadata.get(
                "source",
                "",
            )
        ).strip().lower()

        if actual_source == normalized_source:

            return metadata

    return {
        "source": "Unknown",
        "university": "Unknown",
        "program": "Unknown",
        "chunk_index": "Unknown",
    }


def analyze_eligibility(
    profile: StudentProfile,
    filters: dict | None = None,
    n_results: int = 8,
) -> EligibilityResult:
    """
    Analyze the student's eligibility for a specific
    university/program using retrieved evidence.
    """

    # ==================================================
    # 1. REQUIREMENT-FOCUSED RETRIEVAL QUERIES
    # ==================================================

    queries = [

        f"""
What bachelor's degree, academic field, and academic
background are required for the {profile.target_degree}
in {profile.target_field}?
""",

        f"""
What minimum CGPA, academic grade, ranking, or equivalent
academic performance requirement is stated for the
{profile.target_degree} in {profile.target_field}?
""",

        f"""
What mathematics, programming, computer science, or other
academic prerequisite courses are required for the
{profile.target_degree} in {profile.target_field}?
""",

        f"""
What English language requirement, IELTS score, TOEFL score,
CEFR level, or other language requirement is stated for the
{profile.target_degree} in {profile.target_field}?
""",

        f"""
What application documents are explicitly required for the
{profile.target_degree} in {profile.target_field}?
""",
    ]

    # ==================================================
    # 2. STORAGE FOR RETRIEVED EVIDENCE
    # ==================================================

    all_documents = []
    all_metadatas = []
    all_distances = []

    # ==================================================
    # 3. RETRIEVE EVIDENCE
    # ==================================================

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

                all_documents.append(
                    document
                )

                all_metadatas.append(
                    metadata
                )

                all_distances.append(
                    distance
                )

    # ==================================================
    # 4. REMOVE DUPLICATE CHUNKS
    # ==================================================

    unique_documents = []
    unique_metadatas = []
    unique_distances = []

    seen_chunks = set()

    for document, metadata, distance in zip(
        all_documents,
        all_metadatas,
        all_distances,
    ):

        source = metadata.get(
            "source",
            "Unknown",
        )

        chunk_index = metadata.get(
            "chunk_index",
            "Unknown",
        )

        chunk_key = (
            source,
            chunk_index,
        )

        if chunk_key in seen_chunks:
            continue

        seen_chunks.add(
            chunk_key
        )

        unique_documents.append(
            document
        )

        unique_metadatas.append(
            metadata
        )

        unique_distances.append(
            distance
        )

    # ==================================================
    # 5. NO RELEVANT EVIDENCE
    # ==================================================

    if not unique_documents:

        return EligibilityResult(
            overall_status=(
                "Insufficient Information"
            ),

            summary=(
                "No sufficiently relevant university "
                "admission requirements were found."
            ),
        )

    # ==================================================
    # 6. BUILD EVIDENCE CONTEXT
    # ==================================================

    context_parts = []

    for i, (
        document,
        metadata,
        distance,
    ) in enumerate(
        zip(
            unique_documents,
            unique_metadatas,
            unique_distances,
        ),
        start=1,
    ):

        context_parts.append(
            f"""
EVIDENCE {i}

University:
{metadata.get("university", "Unknown")}

Program:
{metadata.get("program", "Unknown")}

Degree Level:
{metadata.get("degree_level", "Unknown")}

Intake:
{metadata.get("intake", "Unknown")}

Document Type:
{metadata.get("document_type", "Unknown")}

Source:
{metadata.get("source", "Unknown")}

Chunk Index:
{metadata.get("chunk_index", "Unknown")}

Retrieval Distance:
{distance}

Document Content:
{document}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # ==================================================
    # 7. BUILD VALID SOURCE LIST
    # ==================================================

    valid_sources = (
        build_evidence_metadata(
            unique_metadatas
        )
    )

    valid_sources_text = "\n".join(
        f"""
Source:
{item["source"]}

University:
{item["university"]}

Program:
{item["program"]}

Chunk Index:
{item["chunk_index"]}
"""
        for item in valid_sources
    )

    # ==================================================
    # 8. STRUCTURED ELIGIBILITY PROMPT
    # ==================================================

    prompt = f"""
You are UniPath AI, an evidence-based university
admission eligibility analyzer.

Your task is to compare the student's profile against
ONLY the university evidence provided below.

DO NOT use outside knowledge.

==================================================
STUDENT PROFILE
==================================================

Name:
{profile.name}

Bachelor Degree:
{profile.bachelor_degree}

Field of Study:
{profile.field_of_study}

Bachelor University:
{profile.university}

CGPA:
{profile.cgpa}

Graduation Year:
{profile.graduation_year}

Target Degree:
{profile.target_degree}

Target Field:
{profile.target_field}

Target Countries:
{profile.target_countries}

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


==================================================
UNIVERSITY DOCUMENT EVIDENCE
==================================================

{context}


==================================================
VALID EVIDENCE SOURCES
==================================================

You may ONLY use the following source filenames
when returning the "source" field:

{valid_sources_text}


==================================================
EVALUATION RULES
==================================================

Evaluate ONLY requirements explicitly supported
by the university evidence.

For every evaluated requirement return:

- requirement
- student_value
- required_value
- status
- explanation
- mandatory
- source
- university
- program

Allowed status values:

- Meets
- Does Not Meet
- Likely Meets
- Unknown


==================================================
MANDATORY RULES
==================================================

"mandatory" must be true ONLY when the evidence
explicitly indicates that the requirement is:

- mandatory
- required
- compulsory
- necessary

If the evidence says:

- recommended
- preferred
- desirable
- optional

then mandatory must be false.

Do NOT convert recommendations into mandatory
requirements.


==================================================
SOURCE RULES
==================================================

For every requirement:

1. The "source" must be EXACTLY one of the source
   filenames provided in VALID EVIDENCE SOURCES.

2. Do NOT invent a filename.

3. "university" and "program" must correspond to
   the selected source evidence.

4. If a requirement cannot be connected to a specific
   source, use:

   "source": "Unknown"

5. Never create a source that is not present
   in the retrieved evidence.


==================================================
IMPORTANT EVIDENCE RULES
==================================================

1. Do NOT invent requirements.

2. Do NOT use general knowledge about university
   admissions.

3. A recommendation is NOT automatically a mandatory
   admission requirement.

4. If something is recommended, describe it as
   recommended.

5. If a requirement is not present in the evidence,
   mark it as Unknown.

6. Do NOT infer a CGPA requirement if the document
   does not explicitly state one.

7. Do NOT infer an IELTS requirement if the document
   does not explicitly state one.

8. Do NOT infer mathematics prerequisites if they are
   not explicitly stated.

9. Do NOT treat the student's skills or projects as
   satisfying an academic requirement unless the
   university evidence explicitly supports that
   interpretation.

10. Application documents explicitly mentioned by
    the university should be placed in
    application_documents.

11. Do NOT place explicitly stated application
    documents inside unknown_requirements.


==================================================
OVERALL STATUS
==================================================

Use:

"Likely Eligible"

when all evaluated mandatory requirements
are satisfied and no evaluated mandatory
requirement is failed.

Use:

"Not Eligible"

when at least one explicitly evaluated
mandatory requirement is not satisfied.

Use:

"Needs Review"

when important requirements cannot be
determined from the available evidence.

Use:

"Insufficient Information"

when there is not enough university evidence
to perform a meaningful evaluation.


==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_status": "...",

    "checks": [
        {{
            "requirement": "...",
            "student_value": "...",
            "required_value": "...",
            "status": "Meets | Does Not Meet | Likely Meets | Unknown",
            "explanation": "...",
            "mandatory": true,
            "source": "...",
            "university": "...",
            "program": "..."
        }}
    ],

    "unknown_requirements": [],

    "application_documents": [],

    "summary": "..."
}}
"""

    # ==================================================
    # 9. CALL GEMINI
    # ==================================================

    response = llm.invoke(
        prompt
    )

    answer = extract_llm_text(
        response
    )

    # ==================================================
    # 10. CLEAN JSON
    # ==================================================

    answer = clean_json_response(
        answer
    )

    # ==================================================
    # 11. PARSE JSON
    # ==================================================

    try:

        data = json.loads(
            answer
        )

    except json.JSONDecodeError:

        return EligibilityResult(
            overall_status="Analysis Error",

            summary=(
                "The AI returned an invalid structured "
                "eligibility result."
            ),
        )

    # ==================================================
    # 12. BUILD REQUIREMENT CHECKS
    # ==================================================

    checks = []

    for item in data.get(
        "checks",
        [],
    ):

        status = normalize_status(
            item.get(
                "status",
                "Unknown",
            )
        )

        source_from_llm = item.get(
            "source",
            "Unknown",
        )

        actual_metadata = (
            find_source_metadata(
                source=source_from_llm,
                metadatas=unique_metadatas,
            )
        )

        # --------------------------------------------------
        # IMPORTANT:
        # We trust the retrieved metadata for source,
        # university, and program rather than blindly
        # trusting Gemini.
        # --------------------------------------------------

        source = actual_metadata.get(
            "source",
            "Unknown",
        )

        university = actual_metadata.get(
            "university",
            item.get(
                "university",
                "Unknown",
            ),
        )

        program = actual_metadata.get(
            "program",
            item.get(
                "program",
                "Unknown",
            ),
        )

        mandatory = normalize_boolean(
            item.get(
                "mandatory",
                False,
            )
        )

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

                status=status,

                explanation=item.get(
                    "explanation",
                    "",
                ),

                mandatory=mandatory,

                source=source,

                university=university,

                program=program,
            )
        )

    # ==================================================
    # 13. REMOVE DUPLICATE REQUIREMENTS
    # ==================================================

    unique_checks = []

    seen_requirements = set()

    for check in checks:

        key = (
            check.requirement
            .strip()
            .lower()
        )

        if key in seen_requirements:
            continue

        seen_requirements.add(
            key
        )

        unique_checks.append(
            check
        )

    # ==================================================
    # 14. BUILD SOURCES
    # ==================================================

    sources = []

    seen_sources = set()

    for check in unique_checks:

        if check.source == "Unknown":
            continue

        source_key = (
            check.source,
            check.university,
            check.program,
        )

        if source_key in seen_sources:
            continue

        seen_sources.add(
            source_key
        )

        sources.append(
            {
                "filename": check.source,
                "university": check.university,
                "program": check.program,
            }
        )

    # ==================================================
    # 15. RETURN FINAL RESULT
    # ==================================================

    return EligibilityResult(

        overall_status=data.get(
            "overall_status",
            "Needs Review",
        ),

        checks=unique_checks,

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

        sources=sources,
    )

