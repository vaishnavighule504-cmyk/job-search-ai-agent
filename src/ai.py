import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Read from Streamlit Secrets first, then fallback to environment variables
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-3.5-flash")


def analyze_job(job):

    prompt = f"""
You are an expert career coach.

Analyze this job.

Job Title:
{job.get("job_title")}

Company:
{job.get("employer_name")}

Location:
{job.get("job_city")}

Description:
{job.get("job_description")}

Give the response in markdown.

Include:

## Job Summary

## Required Skills

## Who Should Apply

## Interview Preparation Tips

## Resume Improvement Tips

Keep the response concise.
"""

    response = model.generate_content(prompt)

    return response.text


def analyze_resume_match(resume_text, job):
    """Analyzes the fit between a candidate's resume and a job description using Gemini.

    Args:
        resume_text (str): The plain text extracted from the candidate's resume.
        job (dict): The job listing dictionary containing title, description, company, etc.

    Returns:
        str: A structured analysis in markdown format.
    """
    prompt = f"""
You are an expert ATS (Applicant Tracking System) optimizer and professional career coach.

Analyze the matching compatibility between the candidate's resume and the job description provided below.

### Job Details
- **Title:** {job.get("job_title", "N/A")}
- **Company:** {job.get("employer_name", "N/A")}
- **Location:** {job.get("job_city", "N/A")}
- **Description:** 
{job.get("job_description", "N/A")}

### Candidate's Resume
{resume_text}

---

Provide your analysis in clean, professional Markdown. You MUST structure the response with the following exact heading sections:

## 1. Match Score
Provide a match score between 0 and 100 representing how well the candidate's resume fits the job requirements. Return ONLY the number format, e.g., "Score: 85/100" followed by a 1-2 sentence explanation of the score.

## 2. Matching Skills
List the key skills, technologies, and qualifications required by the job that are clearly present in the candidate's resume. Use bullet points.

## 3. Missing Skills
List the key skills, technologies, certifications, or qualifications required or highly preferred by the job that are missing or weak in the candidate's resume. Use bullet points.

## 4. Resume Improvements
Provide specific, actionable suggestions on how the candidate can update their resume to better align with this job (e.g., phrasing, adding missing keywords, restructuring experience).

## 5. Learning Roadmap
Create a brief, sequential learning roadmap (with specific technologies or concepts) to help the candidate bridge the gaps in their missing skills.

## 6. Interview Questions
Provide 3-5 tailored technical or situational interview questions that the candidate is likely to face for this specific role, along with brief tips on how they should structure their answers.
"""

    response = model.generate_content(prompt)
    return response.text