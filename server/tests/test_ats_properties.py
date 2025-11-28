"""
Property-based tests for ATS scoring functionality
Feature: job-application-ats-screening
"""

import pytest
import sys
import os
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ats_service import ATSService


# Strategies for generating test data
resume_data_strategy = st.fixed_dictionaries({
    'name': st.text(min_size=1, max_size=50),
    'email': st.emails(),
    'skills': st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
    'experience_years': st.integers(min_value=0, max_value=40),
    'education': st.lists(st.fixed_dictionaries({
        'degree': st.text(min_size=1, max_size=50),
        'institution': st.text(min_size=1, max_size=50),
        'year': st.text(min_size=4, max_size=4)
    }), min_size=0, max_size=3),
    'work_history': st.lists(st.fixed_dictionaries({
        'title': st.text(min_size=1, max_size=50),
        'company': st.text(min_size=1, max_size=50),
        'duration': st.text(min_size=1, max_size=20),
        'description': st.text(min_size=0, max_size=200)
    }), min_size=0, max_size=5)
})

job_description_strategy = st.text(min_size=50, max_size=500)


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    resume_data=resume_data_strategy,
    job_description=job_description_strategy,
    mock_score=st.floats(min_value=0.0, max_value=100.0)
)
def test_match_score_validity(resume_data, job_description, mock_score):
    """
    Feature: job-application-ats-screening, Property 5: Match score validity
    
    Property: For any ATS comparison result, the match score should be a number 
    between 0 and 100 (inclusive) and include a non-empty explanation.
    
    Validates: Requirements 4.4
    """
    ats = ATSService()
    
    # Mock the Gemini API response
    mock_response = Mock()
    mock_response.text = json.dumps({
        "score": mock_score,
        "explanation": "This is a detailed explanation of the match",
        "strengths": ["Strength 1", "Strength 2"],
        "gaps": ["Gap 1"]
    })
    
    with patch.object(ats.model, 'generate_content', return_value=mock_response):
        result = ats.calculate_match_score(resume_data, job_description)
        
        # Verify score is within valid range
        assert 'score' in result, "Result must contain 'score' field"
        assert isinstance(result['score'], (int, float)), "Score must be a number"
        assert 0.0 <= result['score'] <= 100.0, f"Score must be between 0-100, got {result['score']}"
        
        # Verify explanation exists and is non-empty
        assert 'explanation' in result, "Result must contain 'explanation' field"
        assert isinstance(result['explanation'], str), "Explanation must be a string"
        assert len(result['explanation']) > 0, "Explanation must not be empty"
        
        # Verify optional fields exist
        assert 'strengths' in result, "Result should contain 'strengths' field"
        assert 'gaps' in result, "Result should contain 'gaps' field"
        assert isinstance(result['strengths'], list), "Strengths should be a list"
        assert isinstance(result['gaps'], list), "Gaps should be a list"


@settings(max_examples=50)
@given(
    resume_data=resume_data_strategy,
    job_description=job_description_strategy
)
def test_score_clamping(resume_data, job_description):
    """
    Property: Scores outside 0-100 range are clamped to valid range.
    
    This ensures the system handles edge cases where AI might return invalid scores.
    """
    ats = ATSService()
    
    # Test with out-of-range scores
    test_scores = [-10.0, 150.0, 999.9, -0.1, 100.1]
    
    for invalid_score in test_scores:
        mock_response = Mock()
        mock_response.text = json.dumps({
            "score": invalid_score,
            "explanation": "Test explanation",
            "strengths": [],
            "gaps": []
        })
        
        with patch.object(ats.model, 'generate_content', return_value=mock_response):
            result = ats.calculate_match_score(resume_data, job_description)
            
            # Score should be clamped to 0-100
            assert 0.0 <= result['score'] <= 100.0, f"Score {invalid_score} should be clamped to 0-100 range"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    candidate1_resume=resume_data_strategy,
    candidate2_resume=resume_data_strategy,
    job_description=job_description_strategy
)
def test_fresh_evaluation_per_application(candidate1_resume, candidate2_resume, job_description):
    """
    Feature: job-application-ats-screening, Property 10: Fresh evaluation per application
    
    Property: For any candidate applying to multiple jobs, each application should receive 
    an independent ATS evaluation with a score specific to that job's description.
    
    Validates: Requirements 7.4
    """
    ats = ATSService()
    
    # Mock different scores for different evaluations
    mock_response1 = Mock()
    mock_response1.text = json.dumps({
        "score": 75.0,
        "explanation": "First evaluation",
        "strengths": ["Skill match"],
        "gaps": []
    })
    
    mock_response2 = Mock()
    mock_response2.text = json.dumps({
        "score": 60.0,
        "explanation": "Second evaluation",
        "strengths": ["Experience"],
        "gaps": ["Missing skills"]
    })
    
    with patch.object(ats.model, 'generate_content', side_effect=[mock_response1, mock_response2]):
        # Evaluate same candidate for two different jobs (or different candidates)
        result1 = ats.calculate_match_score(candidate1_resume, job_description)
        result2 = ats.calculate_match_score(candidate2_resume, job_description)
        
        # Each evaluation should return valid results
        assert 'score' in result1 and 'score' in result2
        assert 0.0 <= result1['score'] <= 100.0
        assert 0.0 <= result2['score'] <= 100.0
        
        # Each should have its own explanation
        assert result1['explanation'] != result2['explanation'] or result1['score'] != result2['score']


def test_malformed_ai_response_handling():
    """
    Test that ATS service handles malformed AI responses gracefully.
    """
    ats = ATSService()
    
    resume_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'skills': ['Python'],
        'experience_years': 3,
        'education': [],
        'work_history': []
    }
    
    job_description = "Software Engineer position requiring Python skills"
    
    # Mock a malformed JSON response
    mock_response = Mock()
    mock_response.text = "This is not valid JSON {incomplete"
    
    with patch.object(ats.model, 'generate_content', return_value=mock_response):
        result = ats.calculate_match_score(resume_data, job_description)
        
        # Should return default structure with score 0
        assert isinstance(result, dict)
        assert 'score' in result
        assert result['score'] == 0.0
        assert 'explanation' in result
        assert len(result['explanation']) > 0


def test_missing_fields_in_ai_response():
    """
    Test that ATS service handles missing fields in AI response.
    """
    ats = ATSService()
    
    resume_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'skills': ['Python'],
        'experience_years': 3,
        'education': [],
        'work_history': []
    }
    
    job_description = "Software Engineer position"
    
    # Mock response with missing fields
    mock_response = Mock()
    mock_response.text = json.dumps({
        "score": 75.0
        # Missing explanation, strengths, gaps
    })
    
    with patch.object(ats.model, 'generate_content', return_value=mock_response):
        result = ats.calculate_match_score(resume_data, job_description)
        
        # Should fill in missing fields with defaults
        assert 'explanation' in result
        assert len(result['explanation']) > 0
        assert 'strengths' in result
        assert isinstance(result['strengths'], list)
        assert 'gaps' in result
        assert isinstance(result['gaps'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
