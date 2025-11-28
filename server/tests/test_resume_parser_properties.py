"""
Property-based tests for resume parsing functionality
Feature: job-application-ats-screening
"""

import pytest
import sys
import os
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import Mock, patch
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_parser import ResumeParserService


# Strategy for generating resume-like text
def generate_resume_text(name, email, skills, experience_years):
    """Generate a realistic resume text"""
    return f"""
{name}
{email}

PROFESSIONAL SUMMARY
Experienced professional with {experience_years} years in the industry.

SKILLS
{', '.join(skills)}

EXPERIENCE
Senior Engineer at Tech Company ({experience_years} years)
- Led development projects
- Managed team of engineers

EDUCATION
Bachelor's Degree in Computer Science
University of Technology, 2015
"""


resume_text_strategy = st.builds(
    generate_resume_text,
    name=st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), min_codepoint=65, max_codepoint=122)),
    email=st.emails(),
    skills=st.lists(st.text(min_size=2, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))), min_size=1, max_size=10),
    experience_years=st.integers(min_value=0, max_value=40)
)


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(resume_text=resume_text_strategy)
def test_resume_data_extraction_completeness(resume_text):
    """
    Feature: job-application-ats-screening, Property 4: Resume data extraction completeness
    
    Property: For any parsed resume, the extracted data should contain all required fields:
    name, email, skills, experience_years, and education.
    
    Validates: Requirements 4.2, 8.2
    """
    parser = ResumeParserService()
    
    # Mock the Gemini API response to avoid actual API calls
    mock_response = Mock()
    mock_response.text = json.dumps({
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "skills": ["Python", "JavaScript", "AWS"],
        "experience_years": 5,
        "education": [{"degree": "B.Tech", "institution": "MIT", "year": "2018"}],
        "work_history": [{"title": "Engineer", "company": "Tech Corp", "duration": "2018-2023", "description": "Developed software"}]
    })
    
    with patch.object(parser.model, 'generate_content', return_value=mock_response):
        try:
            parsed_data = parser.parse_resume(resume_text)
            
            # Verify all required fields are present
            required_fields = ['name', 'email', 'skills', 'experience_years', 'education']
            for field in required_fields:
                assert field in parsed_data, f"Required field '{field}' must be present in parsed data"
            
            # Verify field types
            assert isinstance(parsed_data['name'], str), "Name should be a string"
            assert isinstance(parsed_data['email'], str), "Email should be a string"
            assert isinstance(parsed_data['skills'], list), "Skills should be a list"
            assert isinstance(parsed_data['experience_years'], int), "Experience years should be an integer"
            assert isinstance(parsed_data['education'], list), "Education should be a list"
            
            # Verify optional fields
            assert 'phone' in parsed_data, "Phone field should be present (even if empty)"
            assert 'work_history' in parsed_data, "Work history field should be present"
            
        except Exception as e:
            # If parsing fails, it should still return a valid structure
            pytest.fail(f"Parser should handle all inputs gracefully: {str(e)}")


@settings(max_examples=50)
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    skills=st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=20),
    exp_years=st.integers(min_value=0, max_value=50)
)
def test_parsed_data_structure_validity(name, email, skills, exp_years):
    """
    Property: Parsed resume data always has valid structure regardless of input.
    
    This ensures the parser returns consistent data structure even with edge cases.
    """
    parser = ResumeParserService()
    
    # Create mock response with the generated data
    mock_response = Mock()
    mock_response.text = json.dumps({
        "name": name,
        "email": email,
        "phone": "",
        "skills": skills,
        "experience_years": exp_years,
        "education": [],
        "work_history": []
    })
    
    with patch.object(parser.model, 'generate_content', return_value=mock_response):
        resume_text = f"{name}\n{email}\nSkills: {', '.join(skills)}\nExperience: {exp_years} years"
        
        parsed_data = parser.parse_resume(resume_text)
        
        # Verify structure
        assert isinstance(parsed_data, dict), "Parsed data should be a dictionary"
        assert len(parsed_data) >= 7, "Parsed data should have at least 7 fields"
        
        # Verify no None values in required fields
        assert parsed_data['name'] is not None
        assert parsed_data['email'] is not None
        assert parsed_data['skills'] is not None
        assert parsed_data['experience_years'] is not None


def test_empty_resume_handling():
    """
    Test that parser handles empty or minimal resume text gracefully.
    """
    parser = ResumeParserService()
    
    mock_response = Mock()
    mock_response.text = json.dumps({
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "experience_years": 0,
        "education": [],
        "work_history": []
    })
    
    with patch.object(parser.model, 'generate_content', return_value=mock_response):
        parsed_data = parser.parse_resume("Minimal text")
        
        # Should still return valid structure
        assert 'name' in parsed_data
        assert 'email' in parsed_data
        assert 'skills' in parsed_data
        assert isinstance(parsed_data['skills'], list)


def test_malformed_json_handling():
    """
    Test that parser handles malformed AI responses gracefully.
    """
    parser = ResumeParserService()
    
    # Mock a malformed JSON response
    mock_response = Mock()
    mock_response.text = "This is not valid JSON {incomplete"
    
    with patch.object(parser.model, 'generate_content', return_value=mock_response):
        parsed_data = parser.parse_resume("Some resume text")
        
        # Should return default structure on JSON parse error
        assert isinstance(parsed_data, dict)
        assert 'name' in parsed_data
        assert 'skills' in parsed_data
        assert isinstance(parsed_data['skills'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
