from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import io
import traceback

from src.helper import extract_text_from_pdf, ask_expert
from src.job_api import fetch_linkedIn_jobs

app = FastAPI(
    title="JagirSathi - Job Finder API",
    description="Upload your resume and find the best job matches from LinkedIn",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResumeAnalysis(BaseModel):
    summary: str
    skills_gap: str
    future_roadmap: str


class JobMatch(BaseModel):
    title: Optional[str]
    companyName: Optional[str]
    location: Optional[str]
    link: Optional[str]


class JobSearchResponse(BaseModel):
    search_terms: str
    jobs: List[JobMatch]
    total_jobs: int


# Serve HTML directly
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JagirSathi - Job Finder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .upload-section {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            margin-bottom: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .upload-section:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }

        .upload-section.dragover {
            border-color: #764ba2;
            background: #e8eaff;
        }

        .file-input {
            display: none;
        }

        .upload-label {
            cursor: pointer;
            display: block;
        }

        .upload-icon {
            font-size: 4em;
            margin-bottom: 15px;
        }

        .upload-text {
            font-size: 1.2em;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .upload-subtext {
            color: #666;
            font-size: 0.95em;
        }

        .file-name {
            margin-top: 15px;
            padding: 10px 20px;
            background: white;
            border-radius: 8px;
            color: #667eea;
            font-weight: 600;
            display: inline-block;
        }

        .options {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }

        .option-group {
            flex: 1;
        }

        .option-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }

        .option-group input,
        .option-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }

        .option-group input:focus,
        .option-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results {
            display: none;
        }

        .results.active {
            display: block;
        }

        .result-section {
            margin-bottom: 30px;
            background: #f8f9ff;
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
        }

        .result-section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .result-content {
            color: #333;
            line-height: 1.8;
            white-space: pre-wrap;
        }

        .job-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #e0e0e0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .job-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .job-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
        }

        .job-company {
            color: #666;
            font-style: italic;
            margin-bottom: 10px;
        }

        .job-location {
            color: #888;
            font-size: 0.95em;
            margin-bottom: 10px;
        }

        .job-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 6px;
            text-decoration: none;
            transition: background 0.3s ease;
        }

        .job-link:hover {
            background: #764ba2;
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 5px solid #c33;
            display: none;
        }

        .error.active {
            display: block;
        }

        .success {
            background: #efe;
            color: #363;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 5px solid #363;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💼 JagirSathi</h1>
            <p>Your Job Finder Companion - Upload Resume & Find Perfect Matches</p>
        </div>

        <div class="content">
            <div class="error" id="error"></div>

            <div class="upload-section" id="uploadSection">
                <label for="fileInput" class="upload-label">
                    <div class="upload-icon">📄</div>
                    <div class="upload-text">Click to upload or drag & drop</div>
                    <div class="upload-subtext">PDF format only (Max 10MB)</div>
                </label>
                <input type="file" id="fileInput" class="file-input" accept=".pdf">
                <div id="fileName" class="file-name" style="display: none;"></div>
            </div>

            <div class="options">
                <div class="option-group">
                    <label for="location">📍 Location</label>
                    <select id="location">
                        <option value="United States">United States</option>
                        <option value="India">India</option>
                        <option value="United Kingdom">United Kingdom</option>
                        <option value="Canada">Canada</option>
                        <option value="Australia">Australia</option>
                        <option value="Germany">Germany</option>
                        <option value="Singapore">Singapore</option>
                        <option value="Remote">Remote</option>
                    </select>
                </div>
                <div class="option-group">
                    <label for="maxResults">🔢 Max Results</label>
                    <input type="number" id="maxResults" value="20" min="5" max="50">
                </div>
            </div>

            <button class="btn" id="analyzeBtn" disabled>Analyze Resume & Find Jobs</button>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing your resume and finding perfect job matches...</p>
                <p style="color: #666; margin-top: 10px;">This may take 20-30 seconds</p>
            </div>

            <div class="results" id="results">
                <div class="success">✅ Analysis Completed Successfully!</div>

                <div class="result-section">
                    <h2>📄 Resume Summary</h2>
                    <div class="result-content" id="summary"></div>
                </div>

                <div class="result-section">
                    <h2>🛠️ Skills Gap Analysis</h2>
                    <div class="result-content" id="skillsGap"></div>
                </div>

                <div class="result-section">
                    <h2>🚀 Future Roadmap</h2>
                    <div class="result-content" id="roadmap"></div>
                </div>

                <div class="result-section">
                    <h2>💼 Job Matches (<span id="jobCount">0</span> found)</h2>
                    <div id="searchTerms" style="margin-bottom: 15px; color: #667eea; font-weight: 600;"></div>
                    <div id="jobs"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const uploadSection = document.getElementById('uploadSection');
        const fileName = document.getElementById('fileName');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const errorDiv = document.getElementById('error');
        const location = document.getElementById('location');
        const maxResults = document.getElementById('maxResults');

        let selectedFile = null;

        // File input change
        fileInput.addEventListener('change', (e) => {
            console.log('File selected:', e.target.files[0]);
            handleFile(e.target.files[0]);
        });

        // Drag and drop
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadSection.classList.add('dragover');
        });

        uploadSection.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadSection.classList.remove('dragover');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadSection.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                console.log('File dropped:', files[0]);
                handleFile(files[0]);
            }
        });

        // Click on upload section to trigger file input
        uploadSection.addEventListener('click', (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        function handleFile(file) {
            console.log('Handling file:', file);
            
            if (!file) {
                console.error('No file provided');
                showError('No file selected');
                return;
            }

            console.log('File type:', file.type);
            console.log('File size:', file.size);

            if (file.type !== 'application/pdf') {
                showError('Please upload a PDF file only');
                return;
            }

            if (file.size > 10 * 1024 * 1024) {
                showError('File size must be less than 10MB');
                return;
            }

            selectedFile = file;
            fileName.textContent = `📄 ${file.name}`;
            fileName.style.display = 'inline-block';
            analyzeBtn.disabled = false;
            hideError();
            console.log('File successfully selected:', file.name);
        }

        analyzeBtn.addEventListener('click', async () => {
            if (!selectedFile) {
                showError('Please select a file first');
                return;
            }

            console.log('Starting analysis for:', selectedFile.name);

            // Hide previous results and errors
            results.classList.remove('active');
            hideError();
            
            // Show loading
            loading.classList.add('active');
            analyzeBtn.disabled = true;

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                console.log('Sending request to API...');
                const response = await fetch(
                    `/api/complete-analysis?location=${encodeURIComponent(location.value)}&max_results=${maxResults.value}`,
                    {
                        method: 'POST',
                        body: formData
                    }
                );

                console.log('Response status:', response.status);

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('API error:', errorData);
                    throw new Error(errorData.detail || 'Analysis failed');
                }

                const data = await response.json();
                console.log('Analysis complete:', data);
                displayResults(data);
            } catch (error) {
                console.error('Error during analysis:', error);
                showError(`Error: ${error.message}`);
            } finally {
                loading.classList.remove('active');
                analyzeBtn.disabled = false;
            }
        });

        function displayResults(data) {
            console.log('Displaying results...');
            
            // Display analysis
            document.getElementById('summary').textContent = data.analysis.summary;
            document.getElementById('skillsGap').textContent = data.analysis.skills_gap;
            document.getElementById('roadmap').textContent = data.analysis.future_roadmap;

            // Display jobs
            const jobsContainer = document.getElementById('jobs');
            document.getElementById('jobCount').textContent = data.job_search.total_jobs;
            document.getElementById('searchTerms').textContent = `Search terms: ${data.job_search.search_terms}`;

            if (data.job_search.jobs.length === 0) {
                jobsContainer.innerHTML = '<p style="color: #888;">No jobs found. Try adjusting your search criteria.</p>';
            } else {
                jobsContainer.innerHTML = data.job_search.jobs.map(job => `
                    <div class="job-card">
                        <div class="job-title">${job.title || 'N/A'}</div>
                        <div class="job-company">at ${job.companyName || 'N/A'}</div>
                        <div class="job-location">📍 ${job.location || 'N/A'}</div>
                        ${job.link ? `<a href="${job.link}" target="_blank" class="job-link">View Job →</a>` : ''}
                    </div>
                `).join('');
            }

            results.classList.add('active');
            results.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function showError(message) {
            console.error('Showing error:', message);
            errorDiv.textContent = message;
            errorDiv.classList.add('active');
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function hideError() {
            errorDiv.classList.remove('active');
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api")
async def root():
    """API Root endpoint"""
    return {
        "message": "Welcome to JagirSathi API",
        "endpoints": {
            "/api/analyze-resume": "POST - Upload and analyze resume",
            "/api/find-jobs": "POST - Find job matches based on resume",
            "/api/complete-analysis": "POST - Complete analysis + job search",
            "/docs": "API Documentation"
        }
    }


@app.post("/api/complete-analysis")
async def complete_analysis(file: UploadFile = File(...), location: str = "United States", max_results: int = 20):
    """Complete resume analysis + job search in one endpoint"""
    
    print(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        file_like = io.BytesIO(content)
        file_like.name = file.filename
        
        resume_text = extract_text_from_pdf(file_like)
        print(f"Extracted text length: {len(resume_text)} characters")
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. The PDF might be empty or image-based.")
        
        print("Generating summary...")
        summary = ask_expert(
            f"Summarize the following resume text in bullet points highlighting skills, education, experience:\n\n{resume_text}",
            max_token=300
        )
        
        print("Generating skills gap analysis...")
        skills_gap = ask_expert(
            f"Based on the following resume summary, identify any potential skills gaps for a software engineering role and suggest ways to address them:\n\n{resume_text}",
            max_token=300
        )
        
        print("Generating future roadmap...")
        future_roadmap = ask_expert(
            f"Based on the following resume summary, suggest a future roadmap for career growth in software engineering:\n\n{resume_text}",
            max_token=300
        )
        
        print("Extracting keywords...")
        keywords = ask_expert(
            f"Extract 2-3 broad job keywords from this resume for job search (e.g., 'Software Engineer', 'Python Developer'). Return ONLY comma-separated keywords, no explanation:\n\n{resume_text}",
            max_token=100
        )
        
        search_terms = keywords.replace("\n", "").strip()
        print(f"Search terms: {search_terms}")
        
        print(f"Fetching jobs for location: {location}")
        linkedin_jobs = fetch_linkedIn_jobs(search_terms, location=location, rows=max_results)
        print(f"Found {len(linkedin_jobs)} jobs")
        
        formatted_jobs = [
            JobMatch(
                title=job.get('title'),
                companyName=job.get('companyName'),
                location=job.get('location'),
                link=job.get('link')
            )
            for job in linkedin_jobs
        ]
        
        return {
            "analysis": {
                "summary": summary,
                "skills_gap": skills_gap,
                "future_roadmap": future_roadmap
            },
            "job_search": {
                "search_terms": search_terms,
                "jobs": formatted_jobs,
                "total_jobs": len(formatted_jobs)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in complete_analysis: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error in complete analysis: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)