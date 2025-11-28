"""
Property-based tests for job management functionality
Feature: job-application-ats-screening
"""

import pytest
import sqlite3
import os
import sys
from hypothesis import given, strategies as st, settings
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection, init_db

# Test database path
TEST_DB_PATH = "test_interviews.db"

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Setup test database before each test"""
    # Override DB_PATH for testing
    import database
    original_db_path = database.DB_PATH
    database.DB_PATH = TEST_DB_PATH
    
    # Remove existing test database
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Initialize test database
    init_db()
    
    yield
    
    # Cleanup
    database.DB_PATH = original_db_path
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


# Strategy for generating valid job data
job_data_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    'location': st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    'job_type': st.sampled_from(['Full-Time', 'Part-Time', 'Contract', 'Internship']),
    'experience_required': st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    'description': st.text(min_size=10, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',)))
})


@settings(max_examples=100)
@given(job_data=job_data_strategy)
def test_job_creation_persistence(job_data):
    """
    Feature: job-application-ats-screening, Property 6: Job creation persistence
    
    Property: For any valid job submission, the job should be stored in the database 
    and retrievable with all submitted fields intact.
    
    Validates: Requirements 1.3, 1.4, 1.5
    """
    # Connect to test database
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Insert job
        cursor.execute('''
            INSERT INTO jobs (title, location, job_type, experience_required, description, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (
            job_data['title'],
            job_data['location'],
            job_data['job_type'],
            job_data['experience_required'],
            job_data['description']
        ))
        job_id = cursor.lastrowid
        conn.commit()
        
        # Retrieve job
        retrieved_job = cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
        
        # Verify job was stored
        assert retrieved_job is not None, "Job should be retrievable after insertion"
        
        # Verify all fields match
        assert retrieved_job['title'] == job_data['title'], "Title should match"
        assert retrieved_job['location'] == job_data['location'], "Location should match"
        assert retrieved_job['job_type'] == job_data['job_type'], "Job type should match"
        assert retrieved_job['experience_required'] == job_data['experience_required'], "Experience required should match"
        assert retrieved_job['description'] == job_data['description'], "Description should match (for ATS matching)"
        assert retrieved_job['is_active'] == 1, "Job should be active by default"
        assert retrieved_job['created_at'] is not None, "Created timestamp should be set"
        
    finally:
        conn.close()


@settings(max_examples=50)
@given(jobs=st.lists(job_data_strategy, min_size=1, max_size=10))
def test_multiple_jobs_persistence(jobs):
    """
    Property: Multiple jobs can be created and all are retrievable with correct data.
    
    This tests that the database can handle multiple job insertions without data corruption.
    """
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        job_ids = []
        
        # Insert all jobs
        for job_data in jobs:
            cursor.execute('''
                INSERT INTO jobs (title, location, job_type, experience_required, description, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (
                job_data['title'],
                job_data['location'],
                job_data['job_type'],
                job_data['experience_required'],
                job_data['description']
            ))
            job_ids.append(cursor.lastrowid)
        
        conn.commit()
        
        # Verify all jobs are retrievable
        retrieved_jobs = cursor.execute('SELECT * FROM jobs WHERE id IN ({})'.format(
            ','.join('?' * len(job_ids))
        ), job_ids).fetchall()
        
        assert len(retrieved_jobs) == len(jobs), "All jobs should be retrievable"
        
        # Verify each job's data
        for i, retrieved_job in enumerate(retrieved_jobs):
            original_job = jobs[i]
            assert retrieved_job['title'] == original_job['title']
            assert retrieved_job['description'] == original_job['description']
            
    finally:
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
