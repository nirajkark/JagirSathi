import fitz
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
api_key = os.getenv("CHAT_GROQ_API")

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes."""
    # Note: We use 'stream' because FastAPI provides file content as bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_expert(prompt, max_token=500):
    if not api_key:
        raise ValueError("CHAT_GROQ_API not found.")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=max_token,
        api_key=api_key
    )
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content