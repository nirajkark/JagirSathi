import fitz
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
api_key = os.getenv("CHAT_GROQ_API")
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(stream=pdf_path.read(), filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    return text

def ask_expert(prompt, max_token=500):
    """Send a prompt to the expert system and get a response."""
    
    # Check if API key exists
    
    if not api_key:
        raise ValueError("CHAT_GROQ_API environment variable not found. Please check your .env file.")
    
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=max_token,
            timeout=None,
            max_retries=2,
            api_key=api_key
        )
        
        response = llm.invoke(
            [{"role": "user", "content": prompt}]
        )
        
        return response.content
    
    except Exception as e:
        raise Exception(f"Error calling Groq API: {str(e)}")
