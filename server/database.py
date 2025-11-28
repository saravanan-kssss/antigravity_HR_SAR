import sqlite3
import os
from datetime import datetime

DB_PATH = "interviews.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Jobs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        location TEXT NOT NULL,
        job_type TEXT NOT NULL,
        experience_required TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Candidates
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        resume_path TEXT NOT NULL,
        resume_text TEXT,
        skills TEXT,
        experience_years INTEGER,
        education TEXT,
        work_history TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Applications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        match_score REAL NOT NULL,
        match_explanation TEXT,
        status TEXT DEFAULT 'pending',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    ''')
    
    # Interviews (existing table)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT,
        candidate_email TEXT,
        started_at TIMESTAMP,
        ended_at TIMESTAMP,
        status TEXT DEFAULT 'in_progress',
        total_score REAL,
        notes TEXT
    )
    ''')
    
    # Add application_id column to interview table if it doesn't exist
    try:
        cursor.execute('ALTER TABLE interview ADD COLUMN application_id INTEGER')
        print("Added application_id column to interview table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("application_id column already exists")
        else:
            raise
    
    # Questions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS question (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER,
        seq INTEGER,
        text TEXT,
        prompt_source TEXT,
        asked_at TIMESTAMP,
        FOREIGN KEY(interview_id) REFERENCES interview(id)
    )
    ''')
    
    # Answers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        interview_id INTEGER,
        recording_path TEXT,
        cropped_recording_path TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds REAL,
        score REAL,
        auto_score_breakdown TEXT,
        verdict TEXT,
        FOREIGN KEY(question_id) REFERENCES question(id),
        FOREIGN KEY(interview_id) REFERENCES interview(id)
    )
    ''')
    
    # Transcript Chunks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcript_chunk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        answer_id INTEGER,
        timestamp TIMESTAMP,
        text TEXT,
        is_final BOOLEAN,
        FOREIGN KEY(answer_id) REFERENCES answer(id)
    )
    ''')
    
    # Proctor Events
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proctor_event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER,
        question_id INTEGER,
        timestamp TIMESTAMP,
        event_type TEXT,
        confidence REAL,
        frame_path TEXT,
        notes TEXT,
        FOREIGN KEY(interview_id) REFERENCES interview(id)
    )
    ''')
    
    # Create indexes for performance
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidate_email ON candidates(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_application_job ON applications(job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_application_candidate ON applications(candidate_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interview_application ON interview(application_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active)')
        print("Created database indexes")
    except sqlite3.OperationalError as e:
        print(f"Index creation note: {e}")
    
    conn.commit()
    conn.close()
    print("Database initialization complete")

if __name__ == "__main__":
    init_db()
