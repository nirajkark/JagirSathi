import streamlit as st
from src.helper import extract_text_from_pdf, ask_expert
from src.job_api import fetch_linkedIn_jobs

st.set_page_config(page_title="JagirSathi - Job Finder", page_icon=":briefcase:")

st.title("JagirSathi - Your Job Finder Companion :briefcase:")
st.markdown("Upload your resume and let JagirSathi find the best job matches for you from LinkedIn and Naukari")
upload_file = st.file_uploader("Upload your Resume (PDF format only)", type=["pdf"])

if upload_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(upload_file)
    with st.spinner("Summarizing your resume..."):
        summary = ask_expert(f"Summarize the following resume text in bullet points highlighting skills, education, experience:\n\n{resume_text}", max_token=300)
    with st.spinner("Finding skills gaps..."):
        skills_gap = ask_expert(f"Based on the following resume summary, identify any potential skills gaps for a software engineering role and suggest ways to address them:\n\n{resume_text}", max_token=300)
    with st.spinner("Future Road Maps..."):
        future_roadmap = ask_expert(f"Based on the following resume summary, suggest a future roadmap for career growth in software engineering:\n\n{resume_text}", max_token=300)
    
    st.markdown("---")
    st.header("📄 Resume Summary")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px;'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px;'>{skills_gap}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px;'>{future_roadmap}</div>", unsafe_allow_html=True)

    st.success("✅ Analysis Completed Successfully!")

    if st.button("Find Job Matches"):
        with st.spinner("Finding job matches..."):
            keywords = ask_expert(f"Extract 2-3 broad job keywords from this resume for job search (e.g., 'Software Engineer', 'Python Developer'). Return ONLY comma-separated keywords, no explanation:\n\n{resume_text}", max_token=100)
            search_terms = keywords.replace("\n", "").strip()
        st.success(f"✅ Job Search Terms Extracted! : {search_terms}")  # Fixed: Added f-string
        with st.spinner("Fetching jobs from LinksedIn..."):
            linkedIn_jobs = fetch_linkedIn_jobs(search_terms, location="United States", rows=20)
        st.success(f"✅ Found {len(linkedIn_jobs)} jobs from LinkedIn!")

        st.markdown("---")
        st.header("💼 Top LinkedIn Jobs ")

        if linkedIn_jobs:
            for job in linkedIn_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")