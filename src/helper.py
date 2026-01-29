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
    import openai

    load_dotenv()
    openai.api_key = os.getenv("CHAT_GROQ_API")

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=max_token,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].text.strip()
