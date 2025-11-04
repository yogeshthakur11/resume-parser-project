# 🤖 AI Resume Parser API

A powerful resume parsing API built with FastAPI and powered by Groq's Llama 3.3 70B model. This intelligent system extracts structured information from resumes in PDF and DOCX formats using advanced Chain-of-Thought prompting techniques.

## 🎯 Features

- **Multi-Format Support**: Parse PDF, DOCX, and DOC files
- **Intelligent Document Detection**: Automatically identifies whether uploaded files are actual resumes
- **Advanced Text Extraction**: Enhanced extraction from headers, footers, tables, and text boxes in DOCX files
- **Chain-of-Thought Prompting**: Systematic step-by-step information extraction for higher accuracy
- **Batch Processing**: Upload and process multiple resumes simultaneously
- **Comprehensive Data Extraction**:
  - Contact Information (Name, Email, Phone, LinkedIn, Location)
  - Education History (Institution, Degree, Field of Study, GPA, Graduation Year)
  - Work Experience (Company, Position, Duration, Description, Location)
  - Technical and Soft Skills
  - Certifications (Name, Issuer, Date)
  - Projects (Name, Description, Technologies, Links)
  - Professional Summary
- **Proper HTTP Status Codes**: RESTful API with appropriate status codes for different scenarios
- **CORS Enabled**: Ready for frontend integration

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **AI Model**: Groq API (Llama 3.3 70B Versatile)
- **Document Processing**: PyPDF2, python-docx
- **Language**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API Key ([Get one here](https://console.groq.com))

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd resume-parser-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 📦 Dependencies

```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-dotenv==1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
groq==0.4.1
```

## 🎮 Usage

### Start the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Root Endpoint
```http
GET /
```
Returns API information and available endpoints.

#### 2. Health Check
```http
GET /health
```
Returns server health status.

#### 3. Parse Resume(s)
```http
POST /parse-resume
```

**Request**: Multipart form-data with one or more files

**Example using cURL** (Single File):
```bash
curl -X POST "http://localhost:8000/parse-resume" \
  -F "files=@resume.pdf"
```

**Example using cURL** (Multiple Files):
```bash
curl -X POST "http://localhost:8000/parse-resume" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.docx"
```

**Example using Python**:
```python
import requests

url = "http://localhost:8000/parse-resume"
files = [
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.docx', 'rb'))
]

response = requests.post(url, files=files)
print(response.json())
```

**Example using JavaScript (Fetch)**:
```javascript
const formData = new FormData();
formData.append('files', fileInput.files[0]);

fetch('http://localhost:8000/parse-resume', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📊 Response Format

### Successful Single File Response (200 OK)
```json
{
  "status": "success",
  "message": "All files processed successfully",
  "total_files": 1,
  "successful": 1,
  "failed": 0,
  "results": {
    "is_resume": true,
    "not_resume_reason": null,
    "filename": "john_doe_resume.pdf",
    "contact_info": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1-234-567-8900",
      "linkedin": "linkedin.com/in/johndoe",
      "location": "San Francisco, CA"
    },
    "education": [
      {
        "institution": "Stanford University",
        "degree": "Bachelor's",
        "field_of_study": "Computer Science",
        "graduation_year": "2020",
        "gpa": "3.8/4.0"
      }
    ],
    "work_experience": [
      {
        "company": "Tech Corp",
        "position": "Software Engineer",
        "duration": "Jan 2020 - Present",
        "description": "Developed scalable web applications",
        "location": "San Francisco, CA"
      }
    ],
    "skills": ["Python", "FastAPI", "Machine Learning", "Docker"],
    "certifications": [
      {
        "name": "AWS Certified Developer",
        "issuer": "Amazon Web Services",
        "date": "2023"
      }
    ],
    "projects": [
      {
        "name": "AI Resume Parser",
        "description": "Built an intelligent resume parsing system",
        "technologies": ["Python", "FastAPI", "Groq"],
        "link": "github.com/johndoe/resume-parser"
      }
    ],
    "summary": "Experienced software engineer with expertise in AI/ML"
  },
  "errors": null
}
```

### Partial Success Response (207 Multi-Status)
```json
{
  "status": "success",
  "message": "Partial success - some files processed successfully",
  "total_files": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    { /* Resume 1 data */ },
    { /* Resume 2 data */ }
  ],
  "errors": [
    {
      "file": "invalid_file.txt",
      "error": "Unsupported file format",
      "status_code": 415
    }
  ]
}
```

## 🔍 HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | All files successfully parsed |
| 207 | Partial success (some succeeded, some failed) |
| 400 | All files failed or no files provided |
| 415 | Unsupported file format |
| 422 | File content extraction error or not a resume |
| 500 | Internal server error |

## 🧠 Chain-of-Thought Prompting

The system uses a systematic 8-step process for information extraction:

1. **Validate Resume**: Verify document is actually a resume
2. **Contact Information**: Extract name, email, phone, LinkedIn, location
3. **Education History**: Identify degrees, institutions, graduation dates
4. **Work Experience**: Parse job titles, companies, durations, responsibilities
5. **Skills**: Extract technical and soft skills
6. **Certifications**: Identify professional certifications
7. **Projects**: Extract project details and technologies
8. **Summary**: Capture professional summary or objective

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |

### Model Configuration

The default model is `llama-3.3-70b-versatile` with:
- Temperature: 0.1 (for consistent outputs)
- Max Tokens: 2000
- Top P: 0.9

You can modify these in the `parse_resume_with_llm()` function.

## 🧪 Testing

Test the API using the included test files or your own resumes:

```bash
# Test with a sample resume
curl -X POST "http://localhost:8000/parse-resume" \
  -F "files=@sample_resume.pdf"
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Error reading DOCX"
- **Solution**: Ensure the DOCX file is not corrupted and follows standard Office format

**Issue**: "Failed to parse LLM response as JSON"
- **Solution**: The AI model returned invalid JSON. This is rare but can happen with very complex resumes. Try again or simplify the resume format.

**Issue**: "Could not extract sufficient text from the file"
- **Solution**: The file might be an image-based PDF. Ensure text is selectable in the PDF.

## 📝 Project Structure

```
resume-parser-api/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built as part of the Navtech Python with ML Technical Assessment

## 🙏 Acknowledgments

- **Groq** for providing the powerful Llama 3.3 API
- **FastAPI** for the excellent web framework
- **Anthropic** for inspiration in prompt engineering techniques

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Note**: This project was created as part of a technical assessment to demonstrate proficiency in AI/ML, API development, and document processing.
