"""
Resume Parser API using FastAPI and Groq (Llama 3.2)
Technical Assessment Solution with Chain-of-Thought Prompting
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import json
from pathlib import Path
import tempfile
import os

# Document processing libraries
import PyPDF2
import docx
from groq import Groq

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Parser",
    description="Extract structured information from resumes using Transformer models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client (Free API)
# Get your free API key from: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ============================================
# Pydantic Models for Response Structure
# ============================================

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None

class WorkExperience(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class Certification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None

class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    link: Optional[str] = None

class ResumeData(BaseModel):
    contact_info: ContactInfo
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    projects: List[Project] = []
    summary: Optional[str] = None

# ============================================
# File Processing Functions
# ============================================

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
            text += "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def validate_file_format(filename: str) -> bool:
    """Validate if file format is supported"""
    if not filename:
        print("ERROR: filename is None or empty")
        return False
    
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_ext = Path(filename).suffix.lower()
    
    print(f"DEBUG validate_file_format:")
    print(f"  - filename: '{filename}'")
    print(f"  - extracted extension: '{file_ext}'")
    print(f"  - is valid: {file_ext in allowed_extensions}")
    
    return file_ext in allowed_extensions

def extract_text_from_file(file_path: str, filename: str) -> str:
    """Route to appropriate text extraction based on file type"""
    file_ext = Path(filename).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")

# ============================================
# Chain-of-Thought Prompt Engineering
# ============================================

def create_cot_prompt(resume_text: str) -> str:
    """
    Create a Chain-of-Thought prompt for resume parsing
    This helps the LLM break down the task systematically
    """
    
    prompt = f"""You are an expert resume parser AI. Your task is to extract structured information from the provided resume text using a systematic, step-by-step approach.

**Chain-of-Thought Process:**

Step 1: IDENTIFY CONTACT INFORMATION
- Scan for name (usually at the top)
- Look for email addresses (contains @ symbol)
- Find phone numbers (various formats: +91, (xxx) xxx-xxxx, etc.)
- Locate LinkedIn profile URLs
- Identify location/address if present

Step 2: EXTRACT EDUCATION HISTORY
- Find education section (keywords: Education, Academic, Qualification)
- For each entry, extract:
  * Institution/University name
  * Degree type (Bachelor's, Master's, PhD, etc.)
  * Field of study/Major
  * Graduation year or expected graduation
  * GPA/Percentage if mentioned

Step 3: ANALYZE WORK EXPERIENCE
- Locate work experience section (keywords: Experience, Employment, Work History)
- For each role, extract:
  * Company name
  * Job title/Position
  * Duration (start date - end date or "Present")
  * Key responsibilities and achievements
  * Location if mentioned

Step 4: IDENTIFY SKILLS
- Find skills section (keywords: Skills, Technical Skills, Core Competencies)
- Extract both technical and soft skills
- Include programming languages, tools, frameworks, methodologies

Step 5: EXTRACT CERTIFICATIONS
- Look for certifications section
- Extract certificate name, issuing organization, and date

Step 6: FIND PROJECTS
- Identify projects section
- For each project: name, description, technologies used, links

Step 7: CAPTURE PROFESSIONAL SUMMARY
- Look for summary/objective section at the beginning
- Extract the professional summary or career objective

**RESUME TEXT:**
{resume_text}

**OUTPUT INSTRUCTIONS:**
Now, following the above steps, extract all information and provide ONLY a valid JSON response in this exact format (no additional text or explanation):

{{
  "contact_info": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1234567890",
    "linkedin": "linkedin.com/in/profile",
    "location": "City, Country"
  }},
  "education": [
    {{
      "institution": "University Name",
      "degree": "Bachelor's/Master's",
      "field_of_study": "Computer Science",
      "graduation_year": "2023",
      "gpa": "3.8/4.0"
    }}
  ],
  "work_experience": [
    {{
      "company": "Company Name",
      "position": "Job Title",
      "duration": "Jan 2020 - Dec 2022",
      "description": "Key responsibilities and achievements",
      "location": "City, Country"
    }}
  ],
  "skills": ["Python", "Machine Learning", "FastAPI", "etc"],
  "certifications": [
    {{
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date": "2023"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Tech1", "Tech2"],
      "link": "github.com/project"
    }}
  ],
  "summary": "Professional summary or objective"
}}

Return ONLY the JSON object, no other text."""

    return prompt

# ============================================
# LLM Processing Function
# ============================================

def parse_resume_with_llm(resume_text: str) -> dict:
    """
    Use Groq API (Llama 3.2) to parse resume with chain-of-thought prompting
    """
    try:
        # Create chain-of-thought prompt
        prompt = create_cot_prompt(resume_text)
        
        # Call Groq API with Llama 3.2 (3B parameter model)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume parser that extracts structured information from resumes. Always respond with valid JSON only, no additional text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # Fast and free model
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=2000,
            top_p=0.9
        )
        
        # Extract response
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Clean response (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse JSON
        parsed_data = json.loads(response_text)
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {response_text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in LLM processing: {str(e)}")

# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "/parse-resume": "POST - Upload and parse resume file",
            "/health": "GET - Health check"
        },
        "supported_formats": ["PDF", "DOCX", "DOC"],
        "model": "llama-3.3-70b-versatile"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "resume-parser"}

@app.post("/parse-resume", response_model=ResumeData)
async def parse_resume(file: UploadFile = File(...)):
    """
    Main endpoint to parse resume file
    
    Args:
        file: Resume file (PDF, DOCX, or DOC format)
    
    Returns:
        JSON with extracted resume information
    """
    
    # DEBUG: Print file information
    print(f"DEBUG - Received file:")
    print(f"  - filename: {file.filename}")
    print(f"  - content_type: {file.content_type}")
    print(f"  - file object: {file}")
    
    # Step 1: Validate file format
    if not validate_file_format(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format for '{file.filename}'. Allowed formats: PDF, DOCX, DOC"
        )
    
    # Step 2: Save uploaded file temporarily
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Step 3: Extract text from file
        resume_text = extract_text_from_file(temp_file_path, file.filename)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the resume. Please check if the file is valid."
            )
        
        # Step 4: Parse resume using LLM with Chain-of-Thought
        parsed_data = parse_resume_with_llm(resume_text)
        
        # Step 5: Return structured response
        return JSONResponse(content=parsed_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # Cleanup temporary file
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

# ============================================
# Run Application
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)