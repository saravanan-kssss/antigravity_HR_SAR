"""
Resume Parser Service
Extracts text from PDF/DOCX files and uses AI to extract structured data
"""

import os
import json
import traceback
from typing import Dict, Optional
import PyPDF2
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


class ResumeParserService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            traceback.print_exc()
            raise Exception(f"Failed to read PDF file: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            traceback.print_exc()
            raise Exception(f"Failed to read DOCX file: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file (PDF or DOCX)"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def parse_resume(self, resume_text: str) -> Dict:
        """
        Use AI to extract structured data from resume text
        
        Returns:
            dict: {
                'name': str,
                'email': str,
                'phone': str,
                'skills': list[str],
                'experience_years': int,
                'education': list[dict],
                'work_history': list[dict]
            }
        """
        try:
            prompt = f"""Extract the following information from this resume text and return it as valid JSON.

Resume Text:
{resume_text}

Extract:
- name: Full name of the candidate
- email: Email address
- phone: Phone number (if available)
- skills: Array of technical and professional skills
- experience_years: Total years of professional experience (as integer, estimate if not explicit)
- education: Array of education entries, each with {{degree, institution, year}}
- work_history: Array of work entries, each with {{title, company, duration, description}}

Return ONLY valid JSON with these exact keys. If information is not found, use empty string for strings, empty array for arrays, or 0 for numbers.

Example format:
{{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "skills": ["Python", "Machine Learning", "AWS"],
  "experience_years": 5,
  "education": [{{"degree": "B.Tech Computer Science", "institution": "MIT", "year": "2018"}}],
  "work_history": [{{"title": "Software Engineer", "company": "Tech Corp", "duration": "2018-2023", "description": "Developed ML models"}}]
}}

Return ONLY the JSON, no additional text."""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response - remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            parsed_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['name', 'email', 'skills', 'experience_years', 'education', 'work_history']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = [] if field in ['skills', 'education', 'work_history'] else (0 if field == 'experience_years' else '')
            
            # Ensure phone exists
            if 'phone' not in parsed_data:
                parsed_data['phone'] = ''
            
            print(f"Successfully parsed resume for: {parsed_data.get('name', 'Unknown')}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            # Return default structure if parsing fails
            return {
                'name': '',
                'email': '',
                'phone': '',
                'skills': [],
                'experience_years': 0,
                'education': [],
                'work_history': []
            }
        except Exception as e:
            print(f"Error parsing resume with AI: {e}")
            traceback.print_exc()
            raise Exception(f"Failed to parse resume: {str(e)}")
    
    def parse_resume_file(self, file_path: str) -> Dict:
        """
        Complete pipeline: Extract text from file and parse into structured data
        
        Args:
            file_path: Path to resume file (PDF or DOCX)
            
        Returns:
            dict: Structured resume data
        """
        # Extract text
        resume_text = self.extract_text(file_path)
        
        if not resume_text or len(resume_text) < 50:
            raise Exception("Resume file appears to be empty or too short")
        
        # Parse with AI
        parsed_data = self.parse_resume(resume_text)
        
        # Store original text
        parsed_data['resume_text'] = resume_text
        
        return parsed_data


# Test function
if __name__ == "__main__":
    parser = ResumeParserService()
    
    # Test with a sample text
    sample_text = """
    John Doe
    john.doe@email.com | +1-555-0123
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp (2020-Present)
    - Developed machine learning models for recommendation systems
    - Led team of 5 engineers
    
    Software Engineer at StartupXYZ (2018-2020)
    - Built REST APIs using Python and FastAPI
    
    EDUCATION
    B.Tech in Computer Science, MIT (2018)
    
    SKILLS
    Python, Machine Learning, AWS, Docker, FastAPI, TensorFlow
    """
    
    result = parser.parse_resume(sample_text)
    print(json.dumps(result, indent=2))
