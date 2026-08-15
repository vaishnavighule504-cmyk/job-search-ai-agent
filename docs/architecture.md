# Careerly AI - System Architecture Documentation

This document describes the structural layout, data flow, design principles, and AI pipelines implemented in Careerly AI.

## 1. System Overview

Careerly AI is an AI-powered job search agent and application tracking system built with Python, Streamlit, and SQLite. The application helps job seekers search for positions, track application statuses, perform resume ATS scoring audits, and generate tailored, safety-compliant resumes.

```mermaid
graph TD
    A[Streamlit User Interface (app.py, src/ui.py)] --> B[SQLite Local Database (src/database.py)]
    A --> C[AI Engine (src/ai.py)]
    A --> D[API Services (src/services.py)]
    A --> E[PDF Export & Compiler (src/export.py)]
    C --> F[Google Gemini API]
    D --> G[JSearch API via RapidAPI]
```

## 2. Directory Structure

```text
├── app.py                # Main Application entry point & router
├── requirements.txt      # Python dependencies
├── run_tests.py          # Custom test suite execution script
├── docs/                 # System documentation & Viva guides
│   ├── architecture.md
│   └── viva.md
├── src/                  # Source Modules
│   ├── ai.py             # Gemini LLM prompts, analysis, & resume tailor
│   ├── database.py       # SQLite connection, migration, & CRUD queries
│   ├── export.py         # FPDF report compiler (Jobs list & Resume PDF)
│   ├── services.py       # RapidAPI JSearch integration & caching
│   ├── ui.py             # Premium UI job cards & resume analysis rendering
│   └── utils.py          # Salary formatter, skills extractor, & similarity engine
└── tests/                # Test Suite
    ├── test_database.py  # Isolated SQLite in-memory CRUD tests
    └── test_utils.py     # Deterministic salary, skills, & overlap tests
```

## 3. Core Architecture Modules

### A. UI and Routing Layer (`app.py`, `src/ui.py`)
- Built entirely on Streamlit.
- Uses session state for state management (`st.session_state`) to maintain resume texts, search results, and page navigation without page reload loops.
- Styled with modern, high-contrast Earthy tones (browns, creams, dark headers) to present a professional UI.

### B. Database Layer (`src/database.py`)
- Employs local SQLite databases (`jobs_tracker.db`) to ensure persistent tracking.
- Contains two primary tables:
  1. `applications`: Tracks saved/applied job posts, their URLs, cities, dates, and full descriptions.
  2. `user_profile`: A single-candidate table (enforced via SQLite checks) to persist personal contact information, roles, locations, remote preferences, notice periods, and education.
- Migrates database columns dynamically (e.g. adding `job_description` to `applications`) to ensure backward compatibility.

### C. The Hybrid Match Engine (`src/utils.py`)
To prevent relying solely on unstable LLM metrics, Careerly AI uses a hybrid scoring mechanism:

$$\text{Final Match Score} = 0.40 \times \text{Skill Overlap} + 0.30 \times \text{Semantic Cosine Similarity} + 0.30 \times \text{Gemini AI Score}$$

- **Skill Overlap (40%)**: Case-insensitive word boundary scan for 100+ standard IT skills (e.g., Python, Docker, Next.js).
- **Semantic Similarity (30%)**: Pure-Python Bag-of-Words Cosine Similarity comparing word frequency vectors of the resume and job description.
- **Gemini Contextual Evaluator (30%)**: A Gemini 3.5 Flash heuristic score parsing the text description.

### D. Resume Tailoring Engine (`src/ai.py`)
- Implements strict constraint prompting to eliminate hallucination.
- Polishes wording, re-orders bullet points, and highlights matching keywords.
- Prohibited from inventing new internships, companies, metrics, or education.

### E. Caching & Service Layer (`src/services.py`)
- Communicates with RapidAPI's JSearch.
- Employs caching mechanisms (`st.cache_data`) to prevent redundant external API hits, respecting rate-limits and saving network bandwidth.
