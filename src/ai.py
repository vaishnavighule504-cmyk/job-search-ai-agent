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