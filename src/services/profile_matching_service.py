
import json

from src.config.llm import llm
from src.models.student_profile import StudentProfile


def extract_llm_text(response) -> str:
    """
    Extract plain text from an LLM response.
    """

    content = response.content

    if isinstance(content, list):

        text = ""

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                text += item.get(
                    "text",
                    "",
                )

        return text.strip()

    return str(content).strip()


def clean_json_response(text: str) -> str:
    """
    Remove markdown code fences if Gemini returns
    JSON inside ```json ... ```.

    Returns the cleaned JSON string.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def parse_match_analysis(
    text: str,
) -> dict:
    """
    Parse the LLM's profile-match response into
    a Python dictionary.
    """

    cleaned_text = clean_json_response(
        text
    )

    try:

        return json.loads(
            cleaned_text
        )

    except json.JSONDecodeError:

        return {
            "overall_match": "Unknown",
            "match_score": 0,
            "academic_match": {
                "status": "UNKNOWN",
                "explanation": (
                    "The profile matching "
                    "analysis could not be parsed."
                ),
            },
            "cgpa_match": {
                "status": "UNKNOWN",
                "explanation": (
                    "The profile matching "
                    "analysis could not be parsed."
                ),
            },
            "prerequisite_match": {
                "status": "UNKNOWN",
                "explanation": (
                    "The profile matching "
                    "analysis could not be parsed."
                ),
            },
            "english_match": {
                "status": "UNKNOWN",
                "explanation": (
                    "The profile matching "
                    "analysis could not be parsed."
                ),
            },
            "technical_match": {
                "status": "UNKNOWN",
                "explanation": (
                    "The profile matching "
                    "analysis could not be parsed."
                ),
            },
            "strong_matches": [],
            "gaps": [],
            "unknowns": [
                "Profile matching response "
                "could not be parsed."
            ],
            "improvements": [],
            "reasoning_summary": (
                "No reliable structured profile "
                "match was produced."
            ),
        }


def validate_match_analysis(
    analysis: dict,
) -> dict:
    """
    Make sure the important profile-match fields
    have safe default values.
    """

    analysis.setdefault(
        "overall_match",
        "Unknown",
    )

    analysis.setdefault(
        "match_score",
        0,
    )

    analysis.setdefault(
        "academic_match",
        {
            "status": "UNKNOWN",
            "explanation": "",
        },
    )

    analysis.setdefault(
        "cgpa_match",
        {
            "status": "UNKNOWN",
            "explanation": "",
        },
    )

    analysis.setdefault(
        "prerequisite_match",
        {
            "status": "UNKNOWN",
            "explanation": "",
        },
    )

    analysis.setdefault(
        "english_match",
        {
            "status": "UNKNOWN",
            "explanation": "",
        },
    )

    analysis.setdefault(
        "technical_match",
        {
            "status": "UNKNOWN",
            "explanation": "",
        },
    )

    analysis.setdefault(
        "strong_matches",
        [],
    )

    analysis.setdefault(
        "gaps",
        [],
    )

    analysis.setdefault(
        "unknowns",
        [],
    )

    analysis.setdefault(
        "improvements",
        [],
    )

    analysis.setdefault(
        "reasoning_summary",
        "",
    )

    # Make sure match_score is numeric.

    try:

        analysis["match_score"] = float(
            analysis["match_score"]
        )

    except (
        TypeError,
        ValueError,
    ):

        analysis["match_score"] = 0

    # Keep score inside 0–100.

    analysis["match_score"] = max(
        0,
        min(
            100,
            analysis["match_score"],
        ),
    )

    return analysis


def match_student_to_program(
    profile: StudentProfile,
    program: dict,
) -> dict:
    """
    Match a student's profile against one
    university program.

    Returns structured JSON instead of a
    raw JSON string.
    """

    requirements = program.get(
        "requirements",
        "No program requirements provided.",
    )

    prompt = f"""
You are UniPath AI, an AI university admission
profile-matching engine.

Your task is to compare a student's profile against
the requirements/evidence of ONE Master's program.

IMPORTANT RULES:

1. Use ONLY the student's provided profile and the
   program requirements/evidence provided below.

2. Do NOT invent university requirements.

3. Do NOT invent student achievements, grades,
   experience, skills, or qualifications.

4. Clearly distinguish:
   - MATCH
   - PARTIAL MATCH
   - GAP
   - UNKNOWN

5. If a requirement is not present in the available
   program evidence, mark it as UNKNOWN.

6. Do not assume that a student's skill automatically
   satisfies a formal university requirement.

7. Do not treat a recommendation as a mandatory
   requirement unless the evidence explicitly says
   it is mandatory.

8. Be critical and realistic.

STUDENT PROFILE
---------------

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

Target Countries:
{", ".join(profile.target_countries)}

Technical Skills:
{", ".join(profile.skills) if profile.skills else "None provided"}

Projects:
{", ".join(profile.projects) if profile.projects else "None provided"}

Work Experience:
{", ".join(profile.work_experience) if profile.work_experience else "None provided"}

English Test:
{profile.english_test or "Not provided"}

English Score:
{profile.english_score if profile.english_score is not None else "Not provided"}


PROGRAM
-------

University:
{program.get("university", "Unknown")}

Program:
{program.get("program", "Unknown")}

Country:
{program.get("country", "Unknown")}

Degree Level:
{program.get("degree_level", "Unknown")}

Intake:
{program.get("intake", "Unknown")}


PROGRAM REQUIREMENTS / EVIDENCE
-------------------------------

{requirements}


TASK
----

Analyze the student's match with this specific program.

Return ONLY valid JSON using exactly this structure:

{{
    "overall_match": "Strong Match | Moderate Match | Weak Match | Unknown",
    "match_score": 0,
    "academic_match": {{
        "status": "MATCH | PARTIAL MATCH | GAP | UNKNOWN",
        "explanation": "..."
    }},
    "cgpa_match": {{
        "status": "MATCH | PARTIAL MATCH | GAP | UNKNOWN",
        "explanation": "..."
    }},
    "prerequisite_match": {{
        "status": "MATCH | PARTIAL MATCH | GAP | UNKNOWN",
        "explanation": "..."
    }},
    "english_match": {{
        "status": "MATCH | PARTIAL MATCH | GAP | UNKNOWN",
        "explanation": "..."
    }},
    "technical_match": {{
        "status": "MATCH | PARTIAL MATCH | GAP | UNKNOWN",
        "explanation": "..."
    }},
    "strong_matches": [],
    "gaps": [],
    "unknowns": [],
    "improvements": [],
    "reasoning_summary": "..."
}}

SCORING:

Academic background: 25%
CGPA: 20%
Prerequisites: 25%
English: 10%
Technical/profile fit: 20%

MATCH = full points
PARTIAL MATCH = approximately half points
GAP = 0 points
UNKNOWN = 0 points

A high technical/profile match must NOT compensate
for a formal mandatory academic requirement that
the student clearly does not meet.

Return JSON only.
"""

    response = llm.invoke(prompt)

    text = extract_llm_text(
        response
    )

    analysis = parse_match_analysis(
        text
    )

    analysis = validate_match_analysis(
        analysis
    )

    return {
        "university": program.get(
            "university",
            "Unknown",
        ),
        "program": program.get(
            "program",
            "Unknown",
        ),
        "country": program.get(
            "country",
            "Unknown",
        ),
        "match_analysis": analysis,
    }


def build_program_requirements(
    eligibility_result,
) -> str:
    """
    Convert eligibility checks into text that can
    be supplied to the profile matching engine.
    """

    parts = []

    for check in eligibility_result.checks:

        parts.append(
            f"""
Requirement:
{check.requirement}

Student Value:
{check.student_value}

Required Value:
{check.required_value}

Status:
{check.status}

Mandatory:
{check.mandatory}

University:
{check.university}

Program:
{check.program}

Source:
{check.source}

Explanation:
{check.explanation}
"""
        )

    if eligibility_result.unknown_requirements:

        parts.append(
            "\nUNKNOWN REQUIREMENTS:\n"
            + "\n".join(
                f"- {item}"
                for item in
                eligibility_result.unknown_requirements
            )
        )

    return "\n".join(parts)


def match_profile_to_program(
    profile: StudentProfile,
    program: dict,
    eligibility_result,
) -> dict:
    """
    Match the student's profile against the
    eligibility evidence of a program.
    """

    requirements = build_program_requirements(
        eligibility_result
    )

    program_with_requirements = {
        **program,
        "requirements": requirements,
    }

    return match_student_to_program(
        profile=profile,
        program=program_with_requirements,
    )

