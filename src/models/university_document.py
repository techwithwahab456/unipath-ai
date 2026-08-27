from dataclasses import dataclass


@dataclass
class UniversityDocument:

    filename: str
    file_path: str

    university: str
    country: str
    program: str

    degree_level: str
    intake: str

    document_type: str