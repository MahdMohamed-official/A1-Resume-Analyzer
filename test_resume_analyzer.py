"""
test_resume_analyzer.py
------------------------
Basic test cases for resume_analyzer.py

Run with:
    python test_resume_analyzer.py
or:
    pytest test_resume_analyzer.py -v
"""

import unittest
from resume_analyzer import extract_skills, analyze_resume


class TestSkillExtraction(unittest.TestCase):

    def test_extracts_basic_skills(self):
        text = "I know Python, SQL and HTML very well."
        skills = extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("SQL", skills)
        self.assertIn("HTML", skills)

    def test_normalizes_variations(self):
        text = "Experienced in ML, JS and python programming."
        skills = extract_skills(text)
        self.assertIn("Machine Learning", skills)
        self.assertIn("JavaScript", skills)
        self.assertIn("Python", skills)

    def test_empty_text_returns_empty_list(self):
        self.assertEqual(extract_skills(""), [])
        self.assertEqual(extract_skills(None), [])

    def test_no_duplicate_skills(self):
        text = "Python python PYTHON Python programming"
        skills = extract_skills(text)
        self.assertEqual(skills.count("Python"), 1)


class TestMatchingSkills(unittest.TestCase):

    def test_matching_skills_found_correctly(self):
        resume = "Skilled in Python, SQL, HTML and Machine Learning."
        job = "Looking for Python, SQL, Docker and AWS experience."
        result = analyze_resume(resume, job)
        self.assertIn("Python", result["matching_skills"])
        self.assertIn("SQL", result["matching_skills"])
        self.assertNotIn("Docker", result["matching_skills"])


class TestMissingSkills(unittest.TestCase):

    def test_missing_skills_found_correctly(self):
        resume = "Skilled in Python, SQL, HTML and Machine Learning."
        job = "Looking for Python, SQL, Docker and AWS experience."
        result = analyze_resume(resume, job)
        self.assertIn("Docker", result["missing_skills"])
        self.assertIn("AWS", result["missing_skills"])
        self.assertNotIn("Python", result["missing_skills"])

    def test_no_missing_skills_message(self):
        resume = "I know Python and SQL."
        job = "We need Python and SQL."
        result = analyze_resume(resume, job)
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(
            result["suggestions"],
            ["Your resume covers the identified job requirements well."]
        )


class TestMatchScore(unittest.TestCase):

    def test_match_score_partial(self):
        resume = "Python, SQL, HTML, Machine Learning"
        job = "Python, SQL, Docker, AWS"
        result = analyze_resume(resume, job)
        # 2 matches (Python, SQL) out of 4 required = 50%
        self.assertEqual(result["match_score"], 50)

    def test_match_score_perfect(self):
        resume = "Python and SQL expert."
        job = "Need Python and SQL."
        result = analyze_resume(resume, job)
        self.assertEqual(result["match_score"], 100)

    def test_match_score_zero_when_no_overlap(self):
        resume = "Python and SQL expert."
        job = "Need Docker and AWS."
        result = analyze_resume(resume, job)
        self.assertEqual(result["match_score"], 0)


class TestEmptyJobDescription(unittest.TestCase):

    def test_empty_job_description_returns_zero_score(self):
        resume = "Python, SQL, HTML"
        job = ""
        result = analyze_resume(resume, job)
        self.assertEqual(result["required_skills"], [])
        self.assertEqual(result["match_score"], 0)
        self.assertEqual(result["matching_skills"], [])

    def test_return_dictionary_has_all_required_keys(self):
        result = analyze_resume("Python developer", "Need Python skills")
        expected_keys = {
            "resume_skills", "required_skills", "matching_skills",
            "missing_skills", "match_score", "suggestions"
        }
        self.assertEqual(set(result.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main(verbosity=2)
