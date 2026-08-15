import re
from collections import Counter
import math

def format_salary(job):
    """
    Convert salary to Indian LPA format or format appropriately based on currency and period.
    """
    min_salary = job.get("job_min_salary")
    max_salary = job.get("job_max_salary")
    currency = job.get("job_salary_currency") or "INR"
    period = job.get("job_salary_period") or "YEAR"

    if not min_salary and not max_salary:
        return "Salary Not Disclosed"

    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    sym = symbols.get(currency.upper(), currency)

    if currency.upper() == "INR":
        if period.upper() == "YEAR":
            if min_salary and max_salary:
                return f"₹ {min_salary/100000:.1f} - {max_salary/100000:.1f} LPA"
            if min_salary:
                return f"₹ {min_salary/100000:.1f} LPA"
            return f"₹ {max_salary/100000:.1f} LPA"
        else:
            period_str = f"/{period.lower()}" if period else ""
            if min_salary and max_salary:
                return f"₹ {min_salary:,.0f} - ₹ {max_salary:,.0f}{period_str}"
            if min_salary:
                return f"₹ {min_salary:,.0f}{period_str}"
            return f"₹ {max_salary:,.0f}{period_str}"
    else:
        period_str = f"/{period.lower()}" if period else ""
        if min_salary and max_salary:
            return f"{sym}{min_salary:,.0f} - {sym}{max_salary:,.0f}{period_str}"
        if min_salary:
            return f"{sym}{min_salary:,.0f}{period_str}"
        return f"{sym}{max_salary:,.0f}{period_str}"

TECHNICAL_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "golang", "go", "rust", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css", "bash", "shell",
    "react", "angular", "vue", "django", "flask", "fastapi", "spring", "spring boot", "laravel", "express", "node.js", "node", "jquery", "bootstrap", "tailwind", "next.js", "nextjs", "nuxt", "ruby on rails", "rails",
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "jenkins", "git", "github", "gitlab", "ansible", "terraform", "ci/cd", "devops", "cloud", "nginx", "apache",
    "machine learning", "ml", "artificial intelligence", "ai", "deep learning", "nlp", "natural language processing", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi", "powerbi", "hadoop", "spark", "hive", "kafka", "elasticsearch",
    "mysql", "postgresql", "postgres", "mongodb", "sqlite", "redis", "cassandra", "oracle", "dynamodb", "mariadb",
    "agile", "scrum", "kanban", "rest api", "rest", "graphql", "microservices", "system design", "data structures", "algorithms", "oop", "testing", "security", "linux", "unix"
]

def extract_skills(text):
    if not text:
        return set()
    text_lower = text.lower()
    found = set()
    for skill in TECHNICAL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if skill.endswith("++") or skill.endswith(".js") or skill.endswith("#"):
            pattern = r"\b" + re.escape(skill)
        if re.search(pattern, text_lower):
            found.add(skill)
    return found

def calculate_cosine_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    words1 = re.findall(r'\w+', text1.lower())
    words2 = re.findall(r'\w+', text2.lower())
    if not words1 or not words2:
        return 0.0
    tf1 = Counter(words1)
    tf2 = Counter(words2)
    all_words = set(tf1.keys()).union(set(tf2.keys()))
    dot_product = sum(tf1[word] * tf2[word] for word in all_words)
    magnitude1 = math.sqrt(sum(tf1[word] ** 2 for word in tf1))
    magnitude2 = math.sqrt(sum(tf2[word] ** 2 for word in tf2))
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def calculate_hybrid_score(resume_text, job_description, gemini_score):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    if len(job_skills) == 0:
        skill_overlap = 1.0
    else:
        skill_overlap = len(resume_skills.intersection(job_skills)) / len(job_skills)

    sem_similarity = calculate_cosine_similarity(resume_text, job_description)

    gemini_scaled = float(gemini_score) / 100.0 if gemini_score else 0.6

    final_score = (0.40 * skill_overlap + 0.30 * sem_similarity + 0.30 * gemini_scaled) * 100

    return {
        "final_score": round(final_score, 1),
        "skill_overlap_pct": round(skill_overlap * 100, 1),
        "semantic_similarity_pct": round(sem_similarity * 100, 1),
        "gemini_score_pct": round(gemini_scaled * 100, 1),
        "matching_skills": sorted(list(resume_skills.intersection(job_skills))),
        "missing_skills": sorted(list(job_skills - resume_skills))
    }

def check_notice_period_compatibility(job_desc, candidate_np):
    if not job_desc:
        return True

    desc_lower = job_desc.lower()

    np_map = {
        "immediate": 0,
        "15 days": 15,
        "30 days": 30,
        "60 days": 60,
        "90 days": 90
    }
    candidate_days = np_map.get(candidate_np.lower(), 90)

    immediate_kws = ["immediate", "join immediately", "joining immediately", "immediate joiner", "start immediately"]
    is_immediate_job = any(kw in desc_lower for kw in immediate_kws)

    match_30 = "30 days" in desc_lower or "1 month" in desc_lower
    match_60 = "60 days" in desc_lower or "2 months" in desc_lower
    match_90 = "90 days" in desc_lower or "3 months" in desc_lower

    if is_immediate_job:
        return candidate_days <= 15
    if match_30:
        return candidate_days <= 30
    if match_60:
        return candidate_days <= 60
    if match_90:
        return candidate_days <= 90

    return True
