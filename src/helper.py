import fitz
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc= fitz.open(strean=pdf_path.read(), filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    return text
def ask_expert(prompt, max_token=500):
    """Send a prompt to the expert system and get a response."""
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        max_tokens=max_token,  # Use the parameter here instead of None
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
        api_key=os.getenv("CHAT_GROQ_API")
    )
    
    response = llm.invoke(
        [{"role": "user", "content": prompt}]
    )
    
    return response.content
def fetch_linkedIn_jobs(search_query, location="Nepal",rows=60):
    
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
def fetch_naukari_jobs(search_query, location="india",rows=60):
    pass