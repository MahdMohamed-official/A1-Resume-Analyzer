import streamlit as st

from pdf_extractor import extract_text_from_pdf
from resume_analyzer import analyze_resume

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
)

# ------------------------------------------------------------------
# Built-in job descriptions for supported roles
# (used only as a fallback when the user selects a supported role
# but leaves the job description box empty)
# ------------------------------------------------------------------
BUILT_IN_JOB_DESCRIPTIONS = {
    "Python Developer": """
We are looking for a Python Developer responsible for managing server-side
application logic. Key responsibilities include writing reusable, testable,
and efficient Python code, integrating user-facing elements with server-side
logic, and integrating data storage solutions.
Required skills: Python, Django, Flask, REST APIs, SQL, Git, OOP concepts,
Unit Testing, Data Structures, Debugging.
""".strip(),
    "Data Analyst": """
We are seeking a Data Analyst to interpret data, analyze results, and
provide ongoing reports. You will develop and implement databases, data
collection systems, and data analytics strategies that optimize
statistical efficiency and quality.
Required skills: Python, SQL, Excel, Power BI, Tableau, Data Visualization,
Statistics, Pandas, NumPy, Data Cleaning.
""".strip(),
    "AI/ML Engineer": """
We are hiring an AI/ML Engineer to design, build, and deploy machine
learning models and pipelines. You will work closely with data scientists
to transform prototypes into production-ready systems.
Required skills: Python, Machine Learning, Deep Learning, TensorFlow,
PyTorch, Scikit-learn, NLP, Data Preprocessing, Model Deployment, SQL.
""".strip(),
    "Web Developer": """
We are looking for a Web Developer to build and maintain responsive
websites and web applications, ensuring high performance and availability.
Required skills: HTML, CSS, JavaScript, React, Node.js, REST APIs, Git,
Responsive Design, SQL, Version Control.
""".strip(),
    "Cybersecurity Analyst": """
We are seeking a Cybersecurity Analyst to protect computer systems and
networks from information breaches. You will monitor networks for security
breaches and conduct vulnerability assessments.
Required skills: Network Security, Penetration Testing, SIEM, Firewalls,
Linux, Python, Risk Assessment, Incident Response, Cryptography.
""".strip(),
}

SUPPORTED_ROLES = list(BUILT_IN_JOB_DESCRIPTIONS.keys())


def render_skill_list(skills, empty_message="None found."):
    """Render a list of skills as badges/text, or a fallback message."""
    if skills:
        st.markdown(
            " ".join(
                f"`{skill}`" for skill in skills
            )
        )
    else:
        st.caption(empty_message)


def main():
    # ------------------------------------------------------------
    # Header
    # ------------------------------------------------------------
    st.title("🤖 AI Resume Analyzer")
    st.markdown(
        "Analyze your resume against a target job and identify your skill gaps."
    )
    st.divider()

    # ------------------------------------------------------------
    # Input section
    # ------------------------------------------------------------
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF only)",
            type=["pdf"],
        )

        st.subheader("🎯 Target Job Role")
        job_role = st.selectbox(
            "Select a job role (optional)",
            options=["-- Select a role --"] + SUPPORTED_ROLES,
        )

    with col_right:
        st.subheader("📝 Job Description")
        job_description = st.text_area(
            "Paste the job description here (optional if a supported role is selected above)",
            height=220,
            placeholder="Paste the job description, or select a supported role on the left "
                        "and leave this blank to use a built-in description.",
        )

    st.divider()
    analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

    # ------------------------------------------------------------
    # Analysis flow
    # ------------------------------------------------------------
    if analyze_clicked:
        # --- Validation ---
        if uploaded_file is None:
            st.error("⚠️ Please upload a resume PDF before analyzing.")
            return

        selected_role = None if job_role == "-- Select a role --" else job_role

        final_job_description = job_description.strip()

        if not final_job_description:
            if selected_role and selected_role in BUILT_IN_JOB_DESCRIPTIONS:
                final_job_description = BUILT_IN_JOB_DESCRIPTIONS[selected_role]
                st.info(f"ℹ️ Using the built-in job description for **{selected_role}**.")
            else:
                st.error(
                    "⚠️ Please enter a job description, or select a supported "
                    "job role to use a built-in description."
                )
                return

        # --- Text extraction ---
        with st.spinner("Extracting text from your resume..."):
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
            except Exception:
                st.error(
                    "❌ Something went wrong while reading the PDF. "
                    "Please try a different file."
                )
                return

        if not resume_text:
            st.error(
                "Could not extract text from this PDF. Please upload a text-based PDF."
            )
            return

        # --- Analysis ---
        with st.spinner("Analyzing your resume..."):
            try:
                result = analyze_resume(resume_text, final_job_description)
            except Exception:
                st.error(
                    "❌ An error occurred while analyzing the resume. "
                    "Please try again with a different file or job description."
                )
                return

        if not result:
            st.error("❌ No analysis result was returned. Please try again.")
            return

        st.success("✅ Analysis complete!")
        st.divider()

        # ------------------------------------------------------------
        # Result Dashboard
        # ------------------------------------------------------------
        st.header("📊 Resume Match Dashboard")

        match_score = result.get("match_score", 0) or 0

        score_col1, score_col2 = st.columns([1, 2])
        with score_col1:
            st.metric("Resume Match Score", f"{match_score}%")
        with score_col2:
            st.progress(min(max(int(match_score), 0), 100) / 100)

        st.divider()

        # Matching vs Missing Skills
        st.subheader("🧩 Matching vs Missing Skills")
        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:
            st.success("✅ Matching Skills")
            render_skill_list(
                result.get("matching_skills", []),
                empty_message="No matching skills found.",
            )

        with skill_col2:
            st.warning("❗ Missing Skills")
            render_skill_list(
                result.get("missing_skills", []),
                empty_message="No missing skills — great match!",
            )

        st.divider()

        # Resume Skills vs Required Skills
        st.subheader("📋 Resume Skills vs Required Skills")
        req_col1, req_col2 = st.columns(2)

        with req_col1:
            with st.expander("🧑‍💻 Skills Found in Your Resume", expanded=True):
                render_skill_list(
                    result.get("resume_skills", []),
                    empty_message="No skills detected in the resume.",
                )

        with req_col2:
            with st.expander("📌 Skills Required for the Role", expanded=True):
                render_skill_list(
                    result.get("required_skills", []),
                    empty_message="No required skills specified.",
                )

        st.divider()

        # Improvement Suggestions
        st.subheader("💡 Improvement Suggestions")
        suggestions = result.get("suggestions", [])
        if suggestions:
            for suggestion in suggestions:
                st.info(f"👉 {suggestion}")
        else:
            st.caption("No suggestions available.")


if __name__ == "__main__":
    main()