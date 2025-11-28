"""
ATS (Applicant Tracking System) Service
Compares candidate resumes against job descriptions and generates match scores
"""

import os
import json
import traceback
from typing import Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


class ATSService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def calculate_match_score(self, resume_data: Dict, job_description: str) -> Dict:
        """
        Compare candidate resume against job description and generate match score
        
        Args:
            resume_data: Parsed resume data with fields: name, email, skills, experience_years, education, work_history
            job_description: Full job description text
            
        Returns:
            dict: {
                'score': float (0-100),
                'explanation': str,
                'strengths': list[str],
                'gaps': list[str]
            }
        """
        try:
            # Prepare candidate summary
            candidate_summary = f"""
Candidate: {resume_data.get('name', 'Unknown')}
Email: {resume_data.get('email', 'N/A')}
Experience: {resume_data.get('experience_years', 0)} years

Skills: {', '.join(resume_data.get('skills', []))}

Education:
{self._format_education(resume_data.get('education', []))}

Work History:
{self._format_work_history(resume_data.get('work_history', []))}
"""
            
            prompt = f"""You are an ATS (Applicant Tracking System) evaluating a candidate's resume against a job description.

Job Description:
{job_description}

Candidate Profile:
{candidate_summary}

Evaluate this candidate and provide:
1. Match Score (0-100): How well does this candidate match the job requirements?
   - Consider required skills vs candidate skills
   - Experience level match
   - Education requirements
   - Relevant work history
   - Industry experience

2. Detailed Explanation: Provide a comprehensive analysis of the candidate's fit

3. Strengths: List specific strengths that align with the job (3-5 points)

4. Gaps: List areas where the candidate may not fully meet requirements (2-4 points)

Scoring Guidelines:
- 80-100: Excellent match, highly qualified
- 60-79: Good match, qualified with minor gaps
- 50-59: Moderate match, meets basic requirements
- 30-49: Weak match, significant gaps
- 0-29: Poor match, does not meet requirements

Return ONLY valid JSON with this exact structure:
{{
  "score": 75.5,
  "explanation": "Detailed explanation here...",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "gaps": ["Gap 1", "Gap 2"]
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
            result = json.loads(response_text)
            
            # Validate and normalize score
            score = float(result.get('score', 0))
            score = max(0.0, min(100.0, score))  # Clamp between 0-100
            
            # Ensure required fields
            if 'explanation' not in result or not result['explanation']:
                result['explanation'] = "Unable to generate detailed explanation"
            
            if 'strengths' not in result or not isinstance(result['strengths'], list):
                result['strengths'] = []
            
            if 'gaps' not in result or not isinstance(result['gaps'], list):
                result['gaps'] = []
            
            result['score'] = score
            
            print(f"ATS Score calculated: {score}% for {resume_data.get('name', 'Unknown')}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            # Return default low score if parsing fails
            return {
                'score': 0.0,
                'explanation': "Unable to evaluate candidate due to processing error",
                'strengths': [],
                'gaps': ["Unable to assess qualifications"]
            }
        except Exception as e:
            print(f"Error calculating match score: {e}")
            traceback.print_exc()
            raise Exception(f"Failed to calculate match score: {str(e)}")
    
    def _format_education(self, education_list):
        """Format education list for display"""
        if not education_list:
            return "Not specified"
        
        formatted = []
        for edu in education_list:
            if isinstance(edu, dict):
                degree = edu.get('degree', 'Degree')
                institution = edu.get('institution', 'Institution')
                year = edu.get('year', 'Year')
                formatted.append(f"- {degree}, {institution} ({year})")
            else:
                formatted.append(f"- {edu}")
        
        return '\n'.join(formatted) if formatted else "Not specified"
    
    def _format_work_history(self, work_history_list):
        """Format work history for display"""
        if not work_history_list:
            return "Not specified"
        
        formatted = []
        for work in work_history_list:
            if isinstance(work, dict):
                title = work.get('title', 'Position')
                company = work.get('company', 'Company')
                duration = work.get('duration', 'Duration')
                description = work.get('description', '')
                formatted.append(f"- {title} at {company} ({duration})")
                if description:
                    formatted.append(f"  {description}")
            else:
                formatted.append(f"- {work}")
        
        return '\n'.join(formatted) if formatted else "Not specified"


# Test function
if __name__ == "__main__":
    ats = ATSService()
    
    # Sample resume data
    sample_resume = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'skills': ['Python', 'Machine Learning', 'TensorFlow', 'AWS', 'Docker'],
        'experience_years': 5,
        'education': [
            {'degree': 'B.Tech Computer Science', 'institution': 'MIT', 'year': '2018'}
        ],
        'work_history': [
            {
                'title': 'Senior ML Engineer',
                'company': 'Tech Corp',
                'duration': '2020-Present',
                'description': 'Developed ML models for recommendation systems'
            },
            {
                'title': 'Software Engineer',
                'company': 'StartupXYZ',
                'duration': '2018-2020',
                'description': 'Built REST APIs and data pipelines'
            }
        ]
    }
    
    # Sample job description
    sample_jd = """
    Job Title: Machine Learning Engineer (On-site, 2+ Years Experience)
    Location: Chennai
    Job Type: Full-Time, On-Site
    Experience Required: 2+ Years in Machine Learning or related field
    
    Job Description:
    We are seeking a skilled and motivated Machine Learning Engineer with 2+ years of hands-on
    experience to join our on-site team. You will be responsible for designing, developing, and
    deploying ML models that solve real-world problems and improve our product capabilities.
    
    Required Skills:
    - Strong proficiency in Python and ML frameworks (TensorFlow, PyTorch)
    - Experience with cloud platforms (AWS, GCP, or Azure)
    - Understanding of ML algorithms and model deployment
    - Strong analytical thinking and problem-solving skills
    
    Preferred:
    - Experience with Docker and containerization
    - Knowledge of MLOps practices
    - Bachelor's degree in Computer Science or related field
    """
    
    result = ats.calculate_match_score(sample_resume, sample_jd)
    print(json.dumps(result, indent=2))
