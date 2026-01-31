import streamlit as st
from src.helper import extract_text_from_pdf, ask_expert
from src.job_api import fetch_linkedIn_jobs

st.set_page_config(
    page_title="JagirSathi - Job Finder",
    page_icon="💼",
    layout="wide"
)

st.title("JagirSathi - Your Job Finder Companion 💼")
st.markdown(
    "Upload your resume and let **JagirSathi** analyze your profile and find matching jobs from **LinkedIn**."
)

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF only)",
    type=["pdf"]
)

if uploaded_file:
    with st.spinner("📄 Extracting resume text..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("🧠 Generating resume summary..."):
        summary = ask_expert(
            f"""
            Summarize the following resume in bullet points.
            Focus on skills, education, experience, and projects.

            Resume:
            {resume_text}
            """,
            max_token=300
        )

    with st.spinner("🛠️ Identifying skill gaps..."):
        skills_gap = ask_expert(
            f"""
            Identify skill gaps for a Software Engineer role
            and suggest improvements.

            Resume:
            {resume_text}
            """,
            max_token=300
        )

    with st.spinner("🚀 Creating future career roadmap..."):
        future_roadmap = ask_expert(
            f"""
            Suggest a future roadmap for career growth
            in Software Engineering.

            Resume:
            {resume_text}
            """,
            max_token=300
        )

    st.markdown("---")

    st.header("📄 Resume Summary")
    st.markdown(summary)

    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(skills_gap)

    st.header("🚀 Future Roadmap")
    st.markdown(future_roadmap)

    st.success("✅ Resume analysis completed!")

    st.markdown("---")

    if st.button("🔍 Find Job Matches"):
        with st.spinner("🧠 Extracting job search keywords..."):
            keywords = ask_expert(
                f"""
                Extract ONE best job title from this resume
                (example: Software Engineer, Data Scientist).
                Return ONLY the title, no explanation.

                Resume:
                {resume_text}
                """,
                max_token=50
            )

            search_term = keywords.strip().split("\n")[0]

        st.success(f"🔑 Job Search Term: **{search_term}**")

        with st.spinner("🌐 Fetching LinkedIn jobs..."):
            linkedIn_jobs = fetch_linkedIn_jobs(
                search_query=search_term,
                location="United States",
                rows=20
            )

        st.markdown("---")
        st.header("💼 Top LinkedIn Job Matches")

        if linkedIn_jobs:
            for job in linkedIn_jobs:
                st.subheader(job.get("title", "N/A"))
                st.write(f"🏢 **Company:** {job.get('companyName', 'N/A')}")
                st.write(f"📍 **Location:** {job.get('location', 'N/A')}")
                st.write(f"🔗 [View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("⚠️ No jobs found. Try a different resume or keyword.")
