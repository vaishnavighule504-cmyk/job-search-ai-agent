import hashlib
import streamlit as st
from src.ai import analyze_job


def display_job_card(job):
    title = job.get("job_title", "N/A")
    company = job.get("employer_name", "N/A")
    city = job.get("job_city") or "Not specified"
    employment = job.get("job_employment_type", "N/A")
    apply_link = job.get("job_apply_link")

    salary = "Not disclosed"

    if job.get("job_min_salary") and job.get("job_max_salary"):
        salary = f"{job['job_min_salary']} - {job['job_max_salary']}"

    unique_key = hashlib.md5(
        f"{title}_{company}_{city}_{apply_link}".encode("utf-8")
    ).hexdigest()

    with st.container(border=True):

        col1, col2 = st.columns([5, 1])

        with col1:
            st.subheader(title)
            st.write(f"🏢 **Company:** {company}")
            st.write(f"📍 **Location:** {city}")
            st.write(f"💼 **Employment:** {employment}")
            st.write(f"💰 **Salary:** {salary}")

        with col2:
            if apply_link:
                st.link_button("Apply", apply_link)

        col_b1, col_b2 = st.columns(2) if st.session_state.get("resume_text") else (st.columns(1) + [None])

        with col_b1:
            if st.button("✨ Analyze with AI", key=f"ai_{unique_key}", use_container_width=True):
                with st.spinner("Analyzing with Gemini..."):
                    analysis = analyze_job(job)
                st.markdown(analysis)

        if col_b2 is not None:
            with col_b2:
                if st.button("📊 Analyze Resume Fit", key=f"fit_{unique_key}", use_container_width=True):
                    from src.ai import analyze_resume_match
                    with st.spinner("Matching resume with Gemini..."):
                        fit_analysis = analyze_resume_match(st.session_state.resume_text, job)
                    st.markdown(fit_analysis)

        description = job.get("job_description")

        if description:
            with st.expander("Job Description"):
                st.write(description)