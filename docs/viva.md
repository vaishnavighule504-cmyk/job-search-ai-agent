# Careerly AI - Viva (Oral Exam) Preparation Guide

This document contains typical Computer Science & Engineering (CSE) viva-voce questions and model answers to defend the Careerly AI project during academic project reviews.

## 1. Project Concept & Architecture

### Q1. Explain the architecture of your system.
**Answer:** Careerly AI follows a modular Python design pattern separating concerns into:
1. **Frontend Layer (`app.py`, `src/ui.py`)**: Built in Streamlit, responsible for stateful page routing, forms, progress bars, and rendering.
2. **AI Layer (`src/ai.py`)**: Communicates with Google's Gemini 3.5 Flash via the Generative AI SDK, running general ATS audits, keyword optimizations, and interview preparation questions.
3. **Database Layer (`src/database.py`)**: Manages a local SQLite database storing application pipeline pipelines and candidate settings.
4. **Utility Layer (`src/utils.py`)**: Executes deterministic, low-level Python calculations for salary, skills, and cosine text similarity.

### Q2. Why did you choose Streamlit instead of React/Next.js?
**Answer:** Streamlit allowed rapid prototyping of a secure, Python-centric machine learning and natural language processing interface. It keeps the frontend and backend in one language, reducing architectural overhead (like setting up REST API endpoints) and allowing more focus on the core algorithms: PDF extraction, hybrid matching, and LLM prompting.

### Q3. How does your search page work? What API does it use?
**Answer:** The search page takes input keywords and locations, queries the **JSearch API** on RapidAPI to fetch live postings, and caches the results locally using Streamlit’s cache decorator to respect API quotas.

---

## 2. Advanced Algorithms & Logic

### Q4. Describe your hybrid matching score algorithm. How is it calculated?
**Answer:** To guarantee reliability and prevent LLM hallucinations, the Match Score is not just a number returned by Gemini. It is a weighted hybrid calculation:
1. **Deterministic Skill Overlap (40% Weight)**: The engine searches the resume and job description text for a predefined list of 100+ software skills. The score is computed as:
   
   $$\text{Skill Score} = \frac{|\text{Resume Skills} \cap \text{Job Skills}|}{|\text{Job Skills}|} \times 100$$
   
2. **Semantic Cosine Similarity (30% Weight)**: The engine converts both documents into bag-of-words term frequency vectors and calculates the cosine of the angle between them:
   
   $$\text{Cosine Similarity} = \frac{A \cdot B}{\|A\| \|B\|}$$
   
3. **Gemini AI Evaluator (30% Weight)**: Gemini parses contextual nuances (like experience levels and domain alignment) to assign a score.

The three scores are aggregated to compute the final score displayed in the UI.

### Q5. How does notice-period compatibility filtering work?
**Answer:** The candidate specifies their notice period (Immediate, 15 days, 30 days, 60 days, or 90 days) in their Profile. The engine searches the job description text for notice period statements (e.g. "immediate joiner", "1 month notice"). If keywords are found, it checks if the candidate's notice period is less than or equal to the job's requirement. If no notice period is mentioned, the engine does not assume compatibility, thus preventing false positives.

### Q6. How does the salary formatting utility handle international currencies?
**Answer:** The utility reads the minimum/maximum salary, currency code, and period from the API. If the currency is INR and the period is annual (YEAR), it formats the amount to Lakhs Per Annum (LPA) (e.g. `₹ 6.0 - 9.0 LPA`). For other currencies (USD, EUR, GBP) or periods (MONTH, HOUR), it applies international currency symbols and appends the period suffix (e.g. `$45 - $60/hour`).

---

## 3. Data Flow, Privacy & Tests

### Q7. How does the resume tailoring engine prevent hallucination?
**Answer:** The engine uses strict prompt engineering constraints. The LLM is explicitly instructed that it is only allowed to rephrase wording, optimize formatting, and match keywords using details *already present* in the original resume. It is strictly prohibited from inventing companies, certifications, projects, or metrics.

### Q8. How did you test your system? Did you use a real database for tests?
**Answer:** We wrote a deterministic test suite (`tests/`) containing unit tests for formatters, skill extraction, similarity, and database CRUD. To keep the tests isolated, fast, and offline, we mocked the database connection using Python's `unittest.mock.patch` to direct queries to an in-memory SQLite database (`:memory:`), ensuring the local development database remains clean and unchanged.

### Q9. What security/privacy controls are implemented in the app?
**Answer:** In the Profile tab, we implemented a data privacy control center. The user can trigger a purge of all local SQLite databases and delete all uploaded PDF files from the system, reverting the application state immediately.
