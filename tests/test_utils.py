from src.utils import (
    format_salary,
    extract_skills,
    calculate_cosine_similarity,
    calculate_hybrid_score,
    check_notice_period_compatibility
)

def test_format_salary_inr():
    job_inr_year = {"job_min_salary": 600000, "job_max_salary": 900000, "job_salary_currency": "INR", "job_salary_period": "YEAR"}
    assert format_salary(job_inr_year) == "₹ 6.0 - 9.0 LPA"

    job_inr_month = {"job_min_salary": 50000, "job_max_salary": 80000, "job_salary_currency": "INR", "job_salary_period": "MONTH"}
    assert format_salary(job_inr_month) == "₹ 50,000 - ₹ 80,000/month"

def test_format_salary_usd():
    job_usd_hour = {"job_min_salary": 45, "job_max_salary": 60, "job_salary_currency": "USD", "job_salary_period": "HOUR"}
    assert format_salary(job_usd_hour) == "$45 - $60/hour"

def test_extract_skills():
    text = "We are looking for a Python Developer who knows React, AWS and PostgreSQL."
    skills = extract_skills(text)
    assert "python" in skills
    assert "react" in skills
    assert "aws" in skills
    assert "postgresql" in skills or "postgres" in skills
    assert "java" not in skills

def test_calculate_cosine_similarity():
    text1 = "Python developer React developer"
    text2 = "React developer Python developer"
    sim = calculate_cosine_similarity(text1, text2)
    assert abs(sim - 1.0) < 1e-5

    text3 = "AWS engineer cloud"
    sim_none = calculate_cosine_similarity(text1, text3)
    assert sim_none == 0.0

def test_calculate_hybrid_score():
    resume = "Python React developer"
    job_desc = "Looking for Python React developer"
    res = calculate_hybrid_score(resume, job_desc, 80)
    assert res["final_score"] > 50
    assert "python" in res["matching_skills"]

def test_check_notice_period_compatibility():
    assert check_notice_period_compatibility("We need an immediate joiner", "Immediate") is True
    assert check_notice_period_compatibility("Immediate start required", "90 days") is False
    assert check_notice_period_compatibility("Max 30 days notice period", "30 days") is True
    assert check_notice_period_compatibility("Max 30 days notice period", "60 days") is False
    assert check_notice_period_compatibility("We are looking for Python devs", "90 days") is True
    assert check_notice_period_compatibility("", "30 days") is True
