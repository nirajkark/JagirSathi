import fitz
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    Accepts either a file path or a file-like object (BytesIO).
    """
    try:
       
        if isinstance(pdf_file, (str, Path)):
            doc = fitz.open(pdf_file)
        else:
            
            if hasattr(pdf_file, 'read'):
                pdf_file.seek(0)  # Reset file pointer
            doc = fitz.open(stream=pdf_file, filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text()

        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def ask_expert(prompt, max_token=500):
    """Send a prompt to the expert system and get a response."""
    
    api_key = os.getenv("CHAT_GROQ_API")
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