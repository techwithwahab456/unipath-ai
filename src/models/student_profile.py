from pydantic import BaseModel, Field
from typing import List


class StudentProfile(BaseModel):

    name: str

    bachelor_degree: str

    field_of_study: str

    university: str

    cgpa: float

    graduation_year: int

    target_degree: str = "Master's"

    target_field: str

    target_countries: List[str]

    skills: List[str] = Field(default_factory=list)

    projects: List[str] = Field(default_factory=list)

    work_experience: List[str] = Field(default_factory=list)

    english_test: str | None = None

    english_score: float | None = None