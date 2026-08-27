"""
resume_analyzer.py
-------------------
Core AI/NLP backend logic for the AI Resume Analyzer mini project.

Responsibilities:
    - Extract skills from raw text (resume or job description)
    - Compare resume skills vs job-required skills
    - Calculate a Resume Match Score (0-100)
    - Generate simple, explainable improvement suggestions

Approach:
    This uses a transparent, keyword/dictionary-based NLP technique
    (no deep learning, no external ML models). This keeps it fully
    explainable during a viva and easy to complete in one day.
"""

import re

# ---------------------------------------------------------------------------
# 1. SKILL DICTIONARY
# ---------------------------------------------------------------------------
# Each canonical skill maps to a list of variations/synonyms that should all
# be normalized to that one canonical name. Keys are what we return to the
# user; values are the different ways someone might write that skill.

SKILL_VARIATIONS = {
    "Python": ["python", "python programming", "python3", "python 3"],
    "Java": ["java"],
    "C": ["c programming", " c "],  # spaces around 'c' avoid false matches
    "C++": ["c++", "cpp", "c plus plus"],
    "SQL": ["sql", "structured query language"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "JavaScript": ["javascript", "js", "java script"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "node js", "nodejs", "node"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Linux": ["linux", "unix"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo db", "mongo"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Data Science": ["data science"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "cv"],
    "TensorFlow": ["tensorflow", "tensor flow"],
    "PyTorch": ["pytorch", "py torch"],
    "Excel": ["excel", "ms excel", "microsoft excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Communication": ["communication", "communication skills"],
    "Leadership": ["leadership"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Teamwork": ["teamwork", "team work", "collaboration"],
}


def _build_pattern_map():
    """
    Precompute a regex pattern for every variation, mapped to its
    canonical skill name. Using word boundaries (\b) avoids partial-word
    false matches (e.g. "java" inside "javascript").
    """
    pattern_map = []
    for canonical, variations in SKILL_VARIATIONS.items():
        for variation in variations:
            cleaned = variation.strip()
            if not cleaned:
                continue
            pattern = r"\b" + re.escape(cleaned) + r"\b"
            pattern_map.append((re.compile(pattern, re.IGNORECASE), canonical))
    return pattern_map


_PATTERN_MAP = _build_pattern_map()


# ---------------------------------------------------------------------------
# 2. SKILL EXTRACTION
# ---------------------------------------------------------------------------
def extract_skills(text):
    """
    Detect technical and professional skills from a block of text.

    Input:
        text: str

    Returns:
        list[str] - sorted list of unique canonical skill names found.
    """
    if not text or not isinstance(text, str):
        return []

    found = set()
    for pattern, canonical in _PATTERN_MAP:
        if pattern.search(text):
            found.add(canonical)

    return sorted(found)


# ---------------------------------------------------------------------------
# 3. MATCH SCORE CALCULATION
# ---------------------------------------------------------------------------
def _calculate_match_score(matching_skills, required_skills):
    """
    match_score = (matching / required) * 100, rounded to nearest whole number.
    Returns 0 if there are no required skills (avoids divide-by-zero).
    """
    if not required_skills:
        return 0
    score = (len(matching_skills) / len(required_skills)) * 100
    return round(score)


# ---------------------------------------------------------------------------
# 4. SUGGESTIONS
# ---------------------------------------------------------------------------
def _generate_suggestions(missing_skills):
    """
    Build simple, human-readable suggestions from the list of missing skills.
    """
    if not missing_skills:
        return ["Your resume covers the identified job requirements well."]

    return [f"Consider learning {skill}." for skill in missing_skills]


# ---------------------------------------------------------------------------
# 5. MAIN ANALYSIS FUNCTION (this is what Member 2's app.py will call)
# ---------------------------------------------------------------------------
def analyze_resume(resume_text, job_description):
    """
    Input:
        resume_text: str
        job_description: str

    Returns EXACTLY this dictionary structure:
        {
            "resume_skills": [...],
            "required_skills": [...],
            "matching_skills": [...],
            "missing_skills": [...],
            "match_score": 0,
            "suggestions": [...]
        }
    """
    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    resume_skills_set = set(resume_skills)
    required_skills_set = set(required_skills)

    matching_skills = sorted(resume_skills_set & required_skills_set)
    missing_skills = sorted(required_skills_set - resume_skills_set)

    match_score = _calculate_match_score(matching_skills, required_skills)
    suggestions = _generate_suggestions(missing_skills)

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "suggestions": suggestions,
    }


# ---------------------------------------------------------------------------
# Quick manual run (only executes if you run this file directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_resume = """
    I am a B.Tech CSE student skilled in Python, SQL, HTML and Machine Learning.
    I have built projects using Git and have good problem solving skills.
    """
    sample_job = """
    We are looking for a candidate with experience in Python, SQL, Docker,
    AWS, and Machine Learning. Communication skills are a plus.
    """

    result = analyze_resume(sample_resume, sample_job)
    for key, value in result.items():
        print(f"{key}: {value}")
