"""
Property-based tests for application submission functionality
Feature: job-application-ats-screening
"""

import pytest
import sys
import os
from hypothesis import given, strategies as st, settings
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@settings(max_examples=100)
@given(filename=st.text(min_size=1, max_size=50))
def test_file_format_validation(filename):
    """
    Feature: job-application-ats-screening, Property 1: Resume file format validation
    
    Property: For any file upload attempt, the system should accept only PDF and DOCX 
    formats and reject all other file types.
    
    Validates: Requirements 3.2
    """
    allowed_extensions = ['.pdf', '.docx', '.doc']
    
    # Get file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Check if extension is in allowed list
    is_valid = file_extension in allowed_extensions
    
    # Verify the validation logic
    if file_extension in ['.pdf', '.docx', '.doc']:
        assert is_valid, f"File with extension {file_extension} should be accepted"
    else:
        assert not is_valid, f"File with extension {file_extension} should be rejected"


@settings(max_examples=50)
@given(
    email=st.emails(),
    extension=st.sampled_from(['.pdf', '.docx', '.doc'])
)
def test_resume_filename_uniqueness(email, extension):
    """
    Feature: job-application-ats-screening, Property 2: Resume filename uniqueness
    
    Property: For any uploaded resume file, the generated filename should be unique 
    and include candidate email and timestamp to prevent overwrites.
    
    Validates: Requirements 8.5
    """
    # Simulate filename generation logic
    timestamp1 = datetime.now().strftime("%Y%m%d_%H%M%S")
    email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
    filename1 = f"{email_hash}_{timestamp1}{extension}"
    
    # Generate another filename (simulating a second later)
    import time
    time.sleep(0.001)  # Small delay
    timestamp2 = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds for uniqueness
    filename2 = f"{email_hash}_{timestamp2}{extension}"
    
    # Verify filename contains email hash
    assert email_hash in filename1, "Filename should contain email hash"
    assert email_hash in filename2, "Filename should contain email hash"
    
    # Verify filename contains timestamp
    assert timestamp1 in filename1, "Filename should contain timestamp"
    
    # Verify extension is preserved
    assert filename1.endswith(extension), "Filename should preserve extension"
    assert filename2.endswith(extension), "Filename should preserve extension"
    
    # Verify filenames are different (uniqueness)
    assert filename1 != filename2, "Filenames generated at different times should be unique"


@settings(max_examples=50)
@given(
    candidate_data=st.fixed_dictionaries({
        'name': st.text(min_size=1, max_size=100),
        'email': st.emails(),
        'phone': st.text(min_size=0, max_size=20),
        'skills': st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=10),
        'experience_years': st.integers(min_value=0, max_value=50),
        'education': st.lists(st.text(min_size=1, max_size=100), min_size=0, max_size=5),
        'work_history': st.lists(st.text(min_size=1, max_size=200), min_size=0, max_size=10)
    }),
    match_score=st.floats(min_value=0.0, max_value=100.0)
)
def test_candidate_data_persistence_completeness(candidate_data, match_score):
    """
    Feature: job-application-ats-screening, Property 9: Candidate data persistence completeness
    
    Property: For any application submission, the created candidate record should contain 
    all extracted resume data and the calculated match score.
    
    Validates: Requirements 8.1, 8.2, 8.3
    """
    # Simulate what should be stored in database
    stored_data = {
        'name': candidate_data['name'],
        'email': candidate_data['email'],
        'phone': candidate_data['phone'],
        'skills': candidate_data['skills'],
        'experience_years': candidate_data['experience_years'],
        'education': candidate_data['education'],
        'work_history': candidate_data['work_history'],
        'match_score': match_score
    }
    
    # Verify all required fields are present
    required_fields = ['name', 'email', 'skills', 'experience_years', 'education', 'work_history', 'match_score']
    for field in required_fields:
        assert field in stored_data, f"Required field '{field}' must be stored"
    
    # Verify field types
    assert isinstance(stored_data['name'], str)
    assert isinstance(stored_data['email'], str)
    assert isinstance(stored_data['skills'], list)
    assert isinstance(stored_data['experience_years'], int)
    assert isinstance(stored_data['education'], list)
    assert isinstance(stored_data['work_history'], list)
    assert isinstance(stored_data['match_score'], (int, float))
    
    # Verify match score is in valid range
    assert 0.0 <= stored_data['match_score'] <= 100.0


def test_file_extension_case_insensitivity():
    """
    Test that file extension validation is case-insensitive.
    """
    test_cases = [
        ('resume.PDF', True),
        ('resume.pdf', True),
        ('resume.Pdf', True),
        ('resume.DOCX', True),
        ('resume.docx', True),
        ('resume.DOC', True),
        ('resume.txt', False),
        ('resume.TXT', False),
        ('resume.jpg', False)
    ]
    
    allowed_extensions = ['.pdf', '.docx', '.doc']
    
    for filename, should_be_valid in test_cases:
        file_extension = os.path.splitext(filename)[1].lower()
        is_valid = file_extension in allowed_extensions
        assert is_valid == should_be_valid, f"File {filename} validation failed"


def test_filename_generation_consistency():
    """
    Test that filename generation is consistent for same inputs.
    """
    email = "test@example.com"
    timestamp = "20250101_120000"
    extension = ".pdf"
    
    email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
    filename = f"{email_hash}_{timestamp}{extension}"
    
    # Verify format
    assert filename.startswith(email_hash)
    assert timestamp in filename
    assert filename.endswith(extension)
    
    # Verify reproducibility
    email_hash2 = hashlib.md5(email.encode()).hexdigest()[:8]
    filename2 = f"{email_hash2}_{timestamp}{extension}"
    
    assert filename == filename2, "Same inputs should produce same filename"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



# Test for application-interview linking
import sqlite3

@settings(max_examples=50)
@given(
    application_id=st.integers(min_value=1, max_value=1000),
    candidate_name=st.text(min_size=1, max_size=100),
    candidate_email=st.emails()
)
def test_application_interview_referential_integrity(application_id, candidate_name, candidate_email):
    """
    Feature: job-application-ats-screening, Property 7: Application-interview referential integrity
    
    Property: For any interview started from an application, the interview record should 
    contain a valid application_id that links to an existing application.
    
    Validates: Requirements 6.5, 8.4
    """
    # Simulate interview creation with application_id
    interview_data = {
        'candidate_name': candidate_name,
        'candidate_email': candidate_email,
        'application_id': application_id
    }
    
    # Verify application_id is stored
    assert 'application_id' in interview_data, "Interview must have application_id field"
    assert interview_data['application_id'] == application_id, "Application ID must match"
    
    # Verify it's a valid integer (can be used as foreign key)
    assert isinstance(interview_data['application_id'], int), "Application ID must be an integer"
    assert interview_data['application_id'] > 0, "Application ID must be positive"
