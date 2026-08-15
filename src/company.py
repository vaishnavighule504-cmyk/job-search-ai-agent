import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_company_facts_from_jobs(company_name, jobs_list):
    """
    Scans the current job search results for any listings matching the company name
    and extracts factual data.
    """
    factual_info = {
        "found": False,
        "employer_name": company_name,
        "locations": set(),
        "job_titles": set(),
        "employer_website": None,
        "job_types": set(),
    }

    for job in jobs_list:
        employer = job.get("employer_name") or ""
        if company_name.lower() in employer.lower():
            factual_info["found"] = True
            factual_info["employer_name"] = employer # use official name from API

            city = job.get("job_city")
            state = job.get("job_state")
            country = job.get("job_country")
            loc_parts = [p for p in [city, state, country] if p]
            if loc_parts:
                factual_info["locations"].add(", ".join(loc_parts))

            title = job.get("job_title")
            if title:
                factual_info["job_titles"].add(title)

            web = job.get("employer_website")
            if web:
                factual_info["employer_website"] = web

            emp_type = job.get("job_employment_type")
            if emp_type:
                factual_info["job_types"].add(emp_type)

    factual_info["locations"] = list(factual_info["locations"])
    factual_info["job_titles"] = list(factual_info["job_titles"])
    factual_info["job_types"] = list(factual_info["job_types"])
    return factual_info

def generate_company_insights(company_name):
    """
    Uses Gemini to generate structured insights and overview for a company.
    """
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not api_key:
        return "⚠️ Gemini API key not configured. Cannot fetch AI insights."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash")

        prompt = f"""
You are a corporate research analyst and professional career advisor.
Provide a detailed company research overview for: "{company_name}".

Please structure the output with the following markdown headings:

## Company Overview
A concise summary of what the company does, its mission, and its size.

## Industry & Sector
State the primary industry and sectors they operate in.

## Culture & Values
Highlight key cultural traits, workplace environment, and corporate values based on public information.

## AI-Generated Career Insights
- What are the growth prospects for professionals entering this company?
- What are the key skills they look for?
- Suggestions for someone applying here.

## Interview Preparation Tips
Specific, actionable advice on what to expect in their interview process and how to prepare.

Please make sure the response is concise and professional.
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "ResourceExhausted" in str(e) or "429" in str(e):
            return "⚠️ **AI Rate Limit Exceeded**: Gemini rate limit was reached. Please wait a minute and try again."
        return f"⚠️ **AI Insight Error**: Could not generate insights: {e}"
