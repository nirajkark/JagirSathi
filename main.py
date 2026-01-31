import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.helper import extract_text_from_pdf, ask_expert
from src.job_api import fetch_linkedIn_jobs

# Initialize FastAPI app - make sure this is clean
app = FastAPI()

# Make sure your folder is named 'templates'
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(...)):
    try:
        # 1. Read file content into memory
        pdf_content = await file.read()
        
        # 2. Process PDF
        resume_text = extract_text_from_pdf(pdf_content)
        
        # 3. AI Analysis
        summary = ask_expert(f"Summarize this resume in bullet points:\n\n{resume_text}")
        gap = ask_expert(f"Identify skills gaps for SE roles:\n\n{resume_text}")
        
        # 4. Job Search
        keywords = ask_expert(f"Return only 2-3 job titles as comma separated strings for:\n\n{resume_text}", max_token=50)
        jobs = fetch_linkedIn_jobs(keywords.strip(), location="United States", rows=5)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "summary": summary,
            "skills_gap": gap,
            "jobs": jobs,
            "search_terms": keywords,
            "success": True
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)