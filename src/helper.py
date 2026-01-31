import os
import fitz
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("CHAT_GROQ_API")

if not GROQ_API_KEY:
    raise ValueError("CHAT_GROQ_API not found in environment variables")


def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    return text


def ask_expert(prompt, max_token=300):
    """Query Groq LLM"""

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=max_token,
        api_key=GROQ_API_KEY
    )

    response = llm.invoke(
        [{"role": "user", "content": prompt}]
    )

    return response.content.strip()
