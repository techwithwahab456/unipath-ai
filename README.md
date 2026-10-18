# UniPath AI — Agentic University Admission Decision Support System

UniPath AI is an AI-powered university admission decision-support application designed to help students evaluate their academic profiles against university admission requirements. It combines a Flutter mobile interface, a Python backend, Retrieval-Augmented Generation (RAG), and an agentic workflow to provide evidence-based eligibility analysis, program matching, and application guidance.

Rather than relying entirely on a language model's general knowledge, the system retrieves relevant information from university admission documents and uses that evidence to support its analysis.

## Key Features

### 1. Student Academic Profile
- Capture academic background, bachelor's degree, university, CGPA, and graduation year.
- Record target degree, preferred study field, and target countries.
- Include language proficiency, technical skills, projects, and work experience.
- Use the profile as input for program matching and eligibility evaluation.

### 2. Retrieval-Augmented Generation (RAG)
- Ingest university admission documents, including supported PDF files.
- Split documents into smaller text chunks for retrieval.
- Generate semantic embeddings using a sentence-transformer model.
- Store document embeddings and metadata in ChromaDB.
- Retrieve relevant passages for admission-related questions.
- Use retrieved evidence as context for language-model responses.

### 3. Agentic Admission Analysis
- Coordinate multiple admission-analysis steps through an orchestrated workflow.
- Filter programs according to the student's target degree and field.
- Retrieve program-specific admission requirements.
- Analyze eligibility and profile alignment.
- Consolidate results into structured program comparisons and recommendations.

### 4. Evidence-Based Eligibility Assessment
The system evaluates requirements when supporting evidence is available, including:

- Bachelor's degree and academic background.
- CGPA and explicitly stated academic thresholds.
- Required programming, mathematics, and other prerequisite subjects.
- English or French language proficiency.
- Required application documents.

Each evaluated requirement can be classified as:
- **Meets:** the available evidence supports that the requirement is satisfied.
- **Does Not Meet:** the available evidence indicates that it is not satisfied.
- **Likely Meets:** the evidence supports a probable match but is not conclusive.
- **Unknown:** the available evidence is insufficient to determine the result.

The system can return an insufficient-information result when relevant admission evidence cannot be retrieved.

### 5. Program Matching and Ranking
- Compare a student's academic profile with program requirements.
- Identify potential strengths, gaps, and eligibility risks.
- Support program scoring and ranking within the admission-analysis workflow.
- Categorize programs to help students prioritize their application choices.

Ranking and risk labels are decision-support outputs, not guarantees of admission or statistically validated acceptance probabilities.

### 6. Application Checklist and Admission Strategy
- Identify application documents explicitly mentioned in the retrieved requirements.
- Highlight missing information and potential prerequisite gaps.
- Summarize program-specific concerns.
- Help students prioritize suitable options and plan their next application steps.

### 7. Source-Aware Responses
- Preserve university and program metadata with retrieved document passages.
- Track source document and chunk information.
- Associate eligibility findings with the evidence used during analysis.
- Distinguish documented requirements from missing or unverified information.

Source traceability supports verification; it does not independently guarantee that a document is current or that a generated conclusion is correct.
##Screenshots
<img width="572" height="1024" alt="image" src="https://github.com/user-attachments/assets/49c8040e-fc73-4774-a100-6a943e9c4628" />

<img width="572" height="1024" alt="image" src="https://github.com/user-attachments/assets/42026205-414f-43c4-8fdf-c79ab8e640e7" />

<img width="572" height="1024" alt="image" src="https://github.com/user-attachments/assets/7b9cfd52-8887-4bab-95de-df9bdc74dbd7" />

<img width="572" height="1024" alt="image" src="https://github.com/user-attachments/assets/0bac56bb-43e9-4a71-829b-0c4c2b0697e1" />





## System Architecture

**Flutter Mobile App → Python API → Admission Workflow → RAG Retrieval → Language Model → Structured Results → Flutter UI**

The system separates the student-facing interface from the backend responsible for document retrieval, evidence processing, admission analysis, and result generation.

## Technology Stack

| Component | Technology |
|---|---|
| Mobile frontend | Flutter, Dart |
| API backend | Python, FastAPI |
| Retrieval pipeline | Retrieval-Augmented Generation (RAG) |
| Embeddings | Sentence Transformers |
| Vector database | ChromaDB |
| Language model | Google Gemini |
| AI workflow | Agentic orchestration |
| Document processing | PDF text extraction and chunking |

Confirm the actual imports and implementation before retaining every technology in this table, particularly any agent framework used for orchestration.

## Example Workflow

1. The student enters an academic profile.
2. The workflow filters relevant university programs.
3. The retrieval pipeline searches the indexed admission documents.
4. Relevant evidence is passed to the language model.
5. The eligibility analyzer evaluates explicitly documented requirements.
6. The workflow consolidates profile matching, risk analysis, and program recommendations.
7. The application presents the structured results and application checklist.

## Responsible AI Design

University admission decisions have real consequences. UniPath AI is intended to support research and planning rather than replace official admission decisions.

- Do not invent admission requirements when evidence is unavailable.
- Distinguish mandatory requirements from recommended qualifications.
- Mark missing evidence as unknown instead of assuming eligibility.
- Encourage verification against current official university sources.
- Do not interpret program scores as guaranteed admission probabilities.

## Current Scope

The implemented workflow has been tested across eight programs. Before presenting the project as production-ready, validate the current Flutter integration, source freshness, retrieval quality, scoring logic, and end-to-end behavior.

## Future Improvements

- Live synchronization with official university admission pages.
- More robust citation and source-link presentation.
- Automated evaluation of retrieval relevance and answer faithfulness.
- Improved program-ranking calibration and explainability.
- Persistent user profiles and application progress tracking.
- Automated testing, deployment, and monitoring.

## Project Objective

The goal of UniPath AI is to demonstrate how mobile application development, semantic retrieval, large language models, and agentic orchestration can be combined to solve a practical decision-support problem.

**UniPath AI — Making university admission research more structured, transparent, and evidence-driven.**
