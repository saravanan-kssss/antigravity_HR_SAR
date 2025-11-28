import os
import json
import asyncio
import base64
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from database import get_db_connection, init_db

# Initialize DB
init_db()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("data/media", exist_ok=True)
os.makedirs("data/frames", exist_ok=True)

# Mount static files for media
app.mount("/data", StaticFiles(directory="data"), name="data")

# --- Models ---
class InterviewCreate(BaseModel):
    candidate_name: str
    candidate_email: str
    application_id: Optional[int] = None

class QuestionGenerate(BaseModel):
    count: int = 1
    language: str = "English"
    difficulty: str = "Medium"

class ProctorEvent(BaseModel):
    event_type: str
    confidence: float
    frame_base64: Optional[str] = None
    notes: Optional[str] = None
    timestamp: Optional[str] = None

class JobCreate(BaseModel):
    title: str
    location: str
    job_type: str
    experience_required: str
    description: str

class JobUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_required: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ApplicationSubmit(BaseModel):
    job_id: int
    name: str
    email: str

class TranscriptChunk(BaseModel):
    timestamp: str
    text: str
    is_final: bool

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Routes ---

# Jobs Management API
@app.post("/api/jobs")
async def create_job(job: JobCreate):
    """Create a new job posting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO jobs (title, location, job_type, experience_required, description, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (job.title, job.location, job.job_type, job.experience_required, job.description))
    
    job_id = cursor.lastrowid
    conn.commit()
    
    # Fetch the created job
    created_job = cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    
    return {
        "id": created_job['id'],
        "title": created_job['title'],
        "location": created_job['location'],
        "job_type": created_job['job_type'],
        "experience_required": created_job['experience_required'],
        "description": created_job['description'],
        "is_active": bool(created_job['is_active']),
        "created_at": created_job['created_at']
    }

@app.get("/api/jobs")
async def get_jobs(active_only: bool = True):
    """Get all jobs with applicant counts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            j.*,
            COUNT(DISTINCT a.id) as applicant_count
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
    '''
    
    if active_only:
        query += ' WHERE j.is_active = 1'
    
    query += ' GROUP BY j.id ORDER BY j.created_at DESC'
    
    jobs = cursor.execute(query).fetchall()
    conn.close()
    
    return {
        "jobs": [
            {
                "id": job['id'],
                "title": job['title'],
                "location": job['location'],
                "job_type": job['job_type'],
                "experience_required": job['experience_required'],
                "description": job['description'],
                "is_active": bool(job['is_active']),
                "created_at": job['created_at'],
                "applicant_count": job['applicant_count']
            }
            for job in jobs
        ]
    }

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    """Get job details with applicants"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    job = cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get applicants for this job
    applicants = cursor.execute('''
        SELECT 
            a.id as application_id,
            a.match_score,
            a.status,
            a.applied_at,
            c.id as candidate_id,
            c.name,
            c.email
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        WHERE a.job_id = ?
        ORDER BY a.match_score DESC, a.applied_at DESC
    ''', (job_id,)).fetchall()
    
    conn.close()
    
    return {
        "id": job['id'],
        "title": job['title'],
        "location": job['location'],
        "job_type": job['job_type'],
        "experience_required": job['experience_required'],
        "description": job['description'],
        "is_active": bool(job['is_active']),
        "created_at": job['created_at'],
        "applicants": [
            {
                "application_id": app['application_id'],
                "candidate_id": app['candidate_id'],
                "name": app['name'],
                "email": app['email'],
                "match_score": app['match_score'],
                "status": app['status'],
                "applied_at": app['applied_at']
            }
            for app in applicants
        ]
    }

@app.put("/api/jobs/{job_id}")
async def update_job(job_id: int, job_update: JobUpdate):
    """Update job details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if job exists
    existing = cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Build update query dynamically
    updates = []
    values = []
    
    if job_update.title is not None:
        updates.append('title = ?')
        values.append(job_update.title)
    if job_update.location is not None:
        updates.append('location = ?')
        values.append(job_update.location)
    if job_update.job_type is not None:
        updates.append('job_type = ?')
        values.append(job_update.job_type)
    if job_update.experience_required is not None:
        updates.append('experience_required = ?')
        values.append(job_update.experience_required)
    if job_update.description is not None:
        updates.append('description = ?')
        values.append(job_update.description)
    if job_update.is_active is not None:
        updates.append('is_active = ?')
        values.append(1 if job_update.is_active else 0)
    
    if updates:
        values.append(job_id)
        query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    # Fetch updated job
    updated_job = cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    
    return {
        "id": updated_job['id'],
        "title": updated_job['title'],
        "location": updated_job['location'],
        "job_type": updated_job['job_type'],
        "experience_required": updated_job['experience_required'],
        "description": updated_job['description'],
        "is_active": bool(updated_job['is_active']),
        "created_at": updated_job['created_at']
    }

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: int, permanent: bool = False):
    """Delete a job permanently or mark as inactive"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if permanent:
        # Permanent delete - remove from database
        # First check if there are applications
        app_count = cursor.execute(
            'SELECT COUNT(*) FROM applications WHERE job_id = ?', (job_id,)
        ).fetchone()[0]
        
        if app_count > 0:
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot permanently delete job with {app_count} applications. Mark as inactive instead."
            )
        
        cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
        message = "Job permanently deleted"
    else:
        # Soft delete - just mark as inactive
        cursor.execute('UPDATE jobs SET is_active = 0 WHERE id = ?', (job_id,))
        message = "Job marked as inactive"
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    conn.commit()
    conn.close()
    
    return {"status": "deleted", "message": message}

# Applications API
@app.post("/api/applications")
async def submit_application(
    job_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    """Submit job application with resume upload"""
    import hashlib
    from resume_parser import ResumeParserService
    from ats_service import ATSService
    
    # Validate file format
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are accepted")
    
    # Check if job exists
    conn = get_db_connection()
    cursor = conn.cursor()
    
    job = cursor.execute('SELECT * FROM jobs WHERE id = ? AND is_active = 1', (job_id,)).fetchone()
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found or inactive")
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
        filename = f"{email_hash}_{timestamp}{file_extension}"
        file_path = f"data/uploads/{filename}"
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse resume
        parser = ResumeParserService()
        parsed_data = parser.parse_resume_file(file_path)
        
        # Check if candidate exists
        existing_candidate = cursor.execute(
            'SELECT * FROM candidates WHERE email = ?', (email,)
        ).fetchone()
        
        if existing_candidate:
            candidate_id = existing_candidate['id']
            # Update candidate data
            cursor.execute('''
                UPDATE candidates 
                SET name = ?, phone = ?, resume_path = ?, resume_text = ?,
                    skills = ?, experience_years = ?, education = ?, work_history = ?
                WHERE id = ?
            ''', (
                parsed_data.get('name', name),
                parsed_data.get('phone', ''),
                file_path,
                parsed_data.get('resume_text', ''),
                json.dumps(parsed_data.get('skills', [])),
                parsed_data.get('experience_years', 0),
                json.dumps(parsed_data.get('education', [])),
                json.dumps(parsed_data.get('work_history', [])),
                candidate_id
            ))
        else:
            # Create new candidate
            cursor.execute('''
                INSERT INTO candidates 
                (name, email, phone, resume_path, resume_text, skills, experience_years, education, work_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                parsed_data.get('name', name),
                email,
                parsed_data.get('phone', ''),
                file_path,
                parsed_data.get('resume_text', ''),
                json.dumps(parsed_data.get('skills', [])),
                parsed_data.get('experience_years', 0),
                json.dumps(parsed_data.get('education', [])),
                json.dumps(parsed_data.get('work_history', []))
            ))
            candidate_id = cursor.lastrowid
        
        conn.commit()
        
        # Calculate ATS match score
        ats = ATSService()
        match_result = ats.calculate_match_score(parsed_data, job['description'])
        
        # Determine status based on score
        status = 'qualified' if match_result['score'] >= 50 else 'rejected'
        
        # Create application
        cursor.execute('''
            INSERT INTO applications (candidate_id, job_id, match_score, match_explanation, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            candidate_id,
            job_id,
            match_result['score'],
            match_result['explanation'],
            status
        ))
        application_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "application_id": application_id,
            "candidate_id": candidate_id,
            "match_score": match_result['score'],
            "match_explanation": match_result['explanation'],
            "strengths": match_result.get('strengths', []),
            "gaps": match_result.get('gaps', []),
            "status": status,
            "next_step": "assessment" if status == 'qualified' else "rejected"
        }
        
    except Exception as e:
        conn.close()
        print(f"Error processing application: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process application: {str(e)}")

@app.get("/api/applications/{application_id}")
async def get_application(application_id: int):
    """Get application details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    application = cursor.execute('''
        SELECT a.*, c.name, c.email, c.phone, c.skills, c.experience_years, c.education, c.work_history,
               j.title as job_title
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.id = ?
    ''', (application_id,)).fetchone()
    
    if not application:
        conn.close()
        raise HTTPException(status_code=404, detail="Application not found")
    
    conn.close()
    
    return {
        "id": application['id'],
        "candidate": {
            "id": application['candidate_id'],
            "name": application['name'],
            "email": application['email'],
            "phone": application['phone'],
            "skills": json.loads(application['skills']) if application['skills'] else [],
            "experience_years": application['experience_years'],
            "education": json.loads(application['education']) if application['education'] else [],
            "work_history": json.loads(application['work_history']) if application['work_history'] else []
        },
        "job": {
            "id": application['job_id'],
            "title": application['job_title']
        },
        "match_score": application['match_score'],
        "match_explanation": application['match_explanation'],
        "status": application['status'],
        "applied_at": application['applied_at']
    }

@app.get("/api/applications/{application_id}/match-result")
async def get_match_result(application_id: int):
    """Get match result for application"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    application = cursor.execute('''
        SELECT a.*, c.name, j.title as job_title, j.description
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.id = ?
    ''', (application_id,)).fetchone()
    
    if not application:
        conn.close()
        raise HTTPException(status_code=404, detail="Application not found")
    
    conn.close()
    
    return {
        "application_id": application['id'],
        "candidate_name": application['name'],
        "job_title": application['job_title'],
        "match_score": application['match_score'],
        "match_explanation": application['match_explanation'],
        "status": application['status']
    }

@app.get("/api/metrics/overview")
async def get_metrics_overview(range: str = "30d"):
    """Get dashboard KPI metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count total jobs
    total_jobs = cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1").fetchone()[0]
    
    # Count total candidates
    total_candidates = cursor.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    
    # Count completed assessments
    completed = cursor.execute(
        "SELECT COUNT(*) FROM interview WHERE status = 'completed'"
    ).fetchone()[0]
    
    # Calculate average score using same algorithm as assessment page
    # Get all interviews with their answer scores
    interviews = cursor.execute("""
        SELECT 
            i.id,
            (SELECT COALESCE(SUM(score), 0) FROM answer WHERE interview_id = i.id) as calculated_score,
            (SELECT COUNT(*) FROM answer WHERE interview_id = i.id) as answer_count
        FROM interview i
        WHERE i.status = 'completed'
    """).fetchall()
    
    total_score = 0
    total_max_score = 0
    
    for interview in interviews:
        actual_score = interview['calculated_score'] if interview['calculated_score'] > 0 else 0.0
        max_score = interview['answer_count'] * 5.0 if interview['answer_count'] > 0 else 5.0
        total_score += actual_score
        total_max_score += max_score
    
    avg_score = (total_score / total_max_score * 5.0) if total_max_score > 0 else 0.0
    
    conn.close()
    
    return {
        "totalJobs": total_jobs,
        "totalCandidates": total_candidates,
        "completedAssessments": completed,
        "avgScore": round(avg_score, 2),
        "interviewsToday": 2,
        "deltas": {"totalCandidates": 0.12, "avgScore": 0.05}
    }

@app.get("/api/candidates")
async def get_candidates(page: int = 1, limit: int = 20, status: str = "all", search: str = ""):
    """Get paginated candidates list with application data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    offset = (page - 1) * limit
    
    # Get candidates with their latest application and interview status
    query = """
        SELECT 
            c.id,
            c.name,
            c.email,
            c.phone,
            c.experience_years,
            c.created_at as createdAt,
            j.title as appliedRole,
            a.match_score as overallScore,
            a.status as application_status,
            a.applied_at,
            a.id as application_id,
            i.status as interview_status,
            i.id as interview_id
        FROM candidates c
        LEFT JOIN applications a ON c.id = a.candidate_id
        LEFT JOIN jobs j ON a.job_id = j.id
        LEFT JOIN interview i ON a.id = i.application_id
        WHERE 1=1
    """
    
    if search:
        query += f" AND (c.name LIKE '%{search}%' OR c.email LIKE '%{search}%')"
    
    query += f" ORDER BY c.created_at DESC LIMIT {limit} OFFSET {offset}"
    
    candidates = cursor.execute(query).fetchall()
    total = cursor.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    
    conn.close()
    
    # Determine dynamic status
    items = []
    for c in candidates:
        # Determine status based on application and interview
        if c['interview_status'] == 'completed':
            status = 'completed'
        elif c['interview_status'] in ['in_progress', 'started']:
            status = 'in_progress'
        elif c['application_status'] == 'qualified':
            status = 'passed'
        elif c['application_status'] == 'rejected':
            status = 'rejected'
        else:
            status = 'pending'
        
        items.append({
            "id": c['id'],
            "name": c['name'],
            "email": c['email'],
            "phone": c['phone'] or '',
            "appliedRole": c['appliedRole'] or 'N/A',
            "createdAt": c['createdAt'],
            "overallScore": c['overallScore'] or 0,
            "status": status,
            "applicationId": c['application_id'],
            "interviewId": c['interview_id']
        })
    
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total
    }

@app.get("/api/candidates/{candidate_id}")
async def get_candidate_profile(candidate_id: int):
    """Get full candidate profile with resume data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidate = cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,)).fetchone()
    if not candidate:
        conn.close()
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get applications for this candidate
    applications = cursor.execute('''
        SELECT a.*, j.title as job_title
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.candidate_id = ?
        ORDER BY a.applied_at DESC
    ''', (candidate_id,)).fetchall()
    
    # Get interviews for this candidate
    interviews = cursor.execute('''
        SELECT * FROM interview WHERE candidate_email = ?
        ORDER BY started_at DESC
    ''', (candidate['email'],)).fetchall()
    
    conn.close()
    
    return {
        "id": candidate['id'],
        "name": candidate['name'],
        "email": candidate['email'],
        "phone": candidate['phone'],
        "skills": json.loads(candidate['skills']) if candidate['skills'] else [],
        "experience_years": candidate['experience_years'],
        "education": json.loads(candidate['education']) if candidate['education'] else [],
        "work_history": json.loads(candidate['work_history']) if candidate['work_history'] else [],
        "created_at": candidate['created_at'],
        "applications": [
            {
                "id": app['id'],
                "job_title": app['job_title'],
                "match_score": app['match_score'],
                "status": app['status'],
                "applied_at": app['applied_at']
            }
            for app in applications
        ],
        "interviews": [
            {
                "id": interview['id'],
                "status": interview['status'],
                "total_score": interview['total_score'],
                "started_at": interview['started_at']
            }
            for interview in interviews
        ]
    }

@app.get("/api/assessments")
async def get_assessments(page: int = 1, limit: int = 20, status: str = "all"):
    """Get paginated assessments list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    offset = (page - 1) * limit
    
    # Get interviews with candidate name from candidates table (not interview table)
    query = """
        SELECT 
            i.id,
            i.status as interview_status,
            i.started_at as createdAt,
            i.total_score as total_score,
            i.application_id,
            a.match_score,
            a.candidate_id,
            c.name as candidate_name,
            c.email as candidate_email,
            j.title as jobTitle,
            (SELECT COUNT(*) FROM answer WHERE interview_id = i.id AND recording_path IS NOT NULL) as hasRecordings,
            (SELECT COALESCE(SUM(score), 0) FROM answer WHERE interview_id = i.id) as calculated_score,
            (SELECT COUNT(*) FROM answer WHERE interview_id = i.id) as answer_count
        FROM interview i
        LEFT JOIN applications a ON i.application_id = a.id
        LEFT JOIN candidates c ON a.candidate_id = c.id
        LEFT JOIN jobs j ON a.job_id = j.id
        ORDER BY i.started_at DESC
        LIMIT ? OFFSET ?
    """
    
    interviews = cursor.execute(query, (limit, offset)).fetchall()
    total = cursor.execute("SELECT COUNT(*) FROM interview").fetchone()[0]
    
    conn.close()
    
    items = []
    for i in interviews:
        # Determine dynamic status
        if i['interview_status'] == 'completed':
            status = 'completed'
        elif i['interview_status'] in ['in_progress', 'started']:
            status = 'in_progress'
        else:
            status = 'passed'  # If interview exists but not started, they passed ATS
        
        # Use calculated score from answers, fallback to total_score
        actual_score = i['calculated_score'] if i['calculated_score'] > 0 else (i['total_score'] or 0.0)
        max_score = i['answer_count'] * 5.0 if i['answer_count'] > 0 else 5.0
        
        items.append({
            "id": i['id'],
            "candidate": {
                "id": i['candidate_id'] or i['id'],
                "name": i['candidate_name'] or 'Unknown'
            },
            "jobTitle": i['jobTitle'] or 'N/A',
            "matchScore": i['match_score'] or 0.0,
            "score": actual_score,
            "maxScore": max_score,
            "status": status,
            "createdAt": i['createdAt'],
            "hasRecordings": bool(i['hasRecordings'])
        })
    
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total
    }

@app.get("/api/assessments/{assessment_id}")
async def get_assessment_detail(assessment_id: int):
    """Get detailed assessment data for report page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get interview with application and job data
    interview = cursor.execute("""
        SELECT 
            i.*,
            a.match_score,
            a.match_explanation,
            j.title as job_title,
            c.name as candidate_name,
            c.email as candidate_email,
            c.phone as candidate_phone
        FROM interview i
        LEFT JOIN applications a ON i.application_id = a.id
        LEFT JOIN jobs j ON a.job_id = j.id
        LEFT JOIN candidates c ON a.candidate_id = c.id
        WHERE i.id = ?
    """, (assessment_id,)).fetchone()
    
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get questions with answers and transcripts
    questions = cursor.execute("""
        SELECT 
            q.id as question_id,
            q.seq,
            q.text as question_text,
            a.id as answer_id,
            a.recording_path,
            a.cropped_recording_path,
            a.score as answer_score,
            a.verdict,
            a.auto_score_breakdown
        FROM question q
        LEFT JOIN answer a ON q.id = a.question_id
        WHERE q.interview_id = ?
        ORDER BY q.seq
    """, (assessment_id,)).fetchall()
    
    # Get proctoring events
    proctor_events = cursor.execute("""
        SELECT * FROM proctor_event 
        WHERE interview_id = ?
        ORDER BY timestamp
    """, (assessment_id,)).fetchall()
    
    # Calculate metrics from answers
    total_score = 0
    max_score = 0
    good_count = 0
    average_count = 0
    below_count = 0
    
    answers_list = []
    for q in questions:
        score = q['answer_score'] or 0
        max_q_score = 5.0
        max_score += max_q_score
        total_score += score
        
        score_percent = (score / max_q_score * 100) if max_q_score > 0 else 0
        
        if score_percent >= 80:
            good_count += 1
        elif score_percent >= 40:
            average_count += 1
        else:
            below_count += 1
        
        # Get transcript for this answer
        transcript_segments = []
        if q['answer_id']:
            transcript_data = cursor.execute("""
                SELECT timestamp, text, is_final
                FROM transcript_chunk
                WHERE answer_id = ?
                ORDER BY timestamp
            """, (q['answer_id'],)).fetchall()
            transcript_segments = [dict(t) for t in transcript_data]
        
        answers_list.append({
            "id": f"a{q['seq']}",
            "question": q['question_text'] or '',
            "type": "video",
            "mediaId": q['recording_path'],
            "scorePercent": score_percent,
            "score": score,
            "verdict": q['verdict'] or '',
            "transcriptSegments": transcript_segments
        })
    
    conn.close()
    
    overall_score = total_score
    overall_score_percent = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Build topic breakdown (mock for now - would need to parse auto_score_breakdown)
    topic_breakdown = []
    
    # Parse feedback from notes field
    feedback_data = {}
    if interview['notes']:
        try:
            feedback_data = json.loads(interview['notes'])
        except:
            feedback_data = {
                'overall_feedback': interview['notes'],
                'detailed_feedback': interview['notes']
            }
    
    # Get topic breakdown from feedback data
    topic_breakdown = feedback_data.get('topics', [])
    
    return {
        "id": assessment_id,
        "candidate": {
            "id": assessment_id,
            "name": interview['candidate_name'] or interview['candidate_name'] or "Unknown",
            "email": interview['candidate_email'] or interview['candidate_email'] or "N/A",
            "phone": interview['candidate_phone'] or "N/A",
            "position": interview['job_title'] or "N/A"
        },
        "overallScorePercent": round(overall_score_percent, 1),
        "overallScore": round(overall_score, 1),
        "maxScore": round(max_score, 1),
        "topicBreakdown": topic_breakdown,
        "metrics": {
            "good": good_count,
            "average": average_count,
            "below": below_count,
            "warnings": len(proctor_events)
        },
        "feedback": {
            "aiOverall": feedback_data.get('overall_feedback', "Assessment feedback not yet generated."),
            "detailed": feedback_data.get('detailed_feedback', "Detailed feedback not yet generated."),
            "keyStrengths": feedback_data.get('key_strengths', []),
            "areasForImprovement": feedback_data.get('areas_for_improvement', []),
            "confidenceLevel": feedback_data.get('confidence_level', 'N/A'),
            "communicationQuality": feedback_data.get('communication_quality', 'N/A'),
            "suitabilityScore": feedback_data.get('suitability_score', overall_score_percent)
        },
        "answers": answers_list,
        "proctoring": [
            {
                "id": e['id'],
                "timestamp": e['timestamp'],
                "eventType": e['event_type'],
                "confidence": e['confidence'],
                "framePath": e['frame_path'],
                "notes": e['notes']
            }
            for e in proctor_events
        ]
    }

@app.post("/api/assessments/{assessment_id}/recompute")
async def recompute_assessment(assessment_id: int):
    """Recompute assessment scores and feedback"""
    from answer_evaluator import AnswerEvaluator
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if interview exists
    interview = cursor.execute(
        "SELECT * FROM interview WHERE id = ?", (assessment_id,)
    ).fetchone()
    
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    try:
        # Get all answers with questions and transcripts
        answers = cursor.execute("""
            SELECT 
                a.id as answer_id,
                q.id as question_id,
                q.text as question,
                q.seq
            FROM answer a
            JOIN question q ON a.question_id = q.id
            WHERE a.interview_id = ?
            ORDER BY q.seq
        """, (assessment_id,)).fetchall()
        
        if not answers:
            conn.close()
            return {"status": "error", "message": "No answers found to recompute"}
        
        evaluator = AnswerEvaluator()
        
        # Re-evaluate each answer
        for ans in answers:
            # Get transcript
            transcripts = cursor.execute("""
                SELECT text FROM transcript_chunk 
                WHERE answer_id = ? AND is_final = 1
                ORDER BY timestamp
            """, (ans['answer_id'],)).fetchall()
            
            answer_text = ' '.join([t['text'] for t in transcripts])
            
            if answer_text and len(answer_text) >= 5:
                # Evaluate
                evaluation = evaluator.evaluate_answer(
                    question=ans['question'],
                    answer_text=answer_text
                )
                
                # Update answer
                cursor.execute("""
                    UPDATE answer 
                    SET score = ?, verdict = ?, auto_score_breakdown = ?
                    WHERE id = ?
                """, (
                    evaluation['score'],
                    evaluation['verdict'],
                    json.dumps({
                        'strengths': evaluation['strengths'],
                        'weaknesses': evaluation['weaknesses']
                    }),
                    ans['answer_id']
                ))
                
                print(f"Re-evaluated answer {ans['answer_id']}: {evaluation['score']}/5")
        
        conn.commit()
        
        # Get updated answers for overall feedback
        updated_answers = cursor.execute("""
            SELECT 
                a.id as answer_id,
                a.score,
                a.verdict,
                q.text as question
            FROM answer a
            JOIN question q ON a.question_id = q.id
            WHERE a.interview_id = ?
            ORDER BY q.seq
        """, (assessment_id,)).fetchall()
        
        # Prepare data for overall feedback
        answers_data = []
        for ans in updated_answers:
            # Get transcript
            transcripts = cursor.execute("""
                SELECT text FROM transcript_chunk 
                WHERE answer_id = ? AND is_final = 1
                ORDER BY timestamp
            """, (ans['answer_id'],)).fetchall()
            
            answer_text = ' '.join([t['text'] for t in transcripts])
            
            answers_data.append({
                'question': ans['question'],
                'answer_text': answer_text,
                'score': ans['score'] or 0.0,
                'verdict': ans['verdict'] or 'Not evaluated'
            })
        
        # Generate overall feedback
        overall_feedback = evaluator.generate_overall_feedback(answers_data)
        
        # Update interview
        cursor.execute("""
            UPDATE interview 
            SET total_score = ?,
                notes = ?
            WHERE id = ?
        """, (
            overall_feedback['overall_score'],
            json.dumps({
                'overall_feedback': overall_feedback['overall_feedback'],
                'detailed_feedback': overall_feedback['detailed_feedback'],
                'overall_score_percent': overall_feedback['overall_score_percent'],
                'topics': overall_feedback.get('topics', []),
                'key_strengths': overall_feedback.get('key_strengths', []),
                'areas_for_improvement': overall_feedback.get('areas_for_improvement', []),
                'confidence_level': overall_feedback.get('confidence_level', 'N/A'),
                'communication_quality': overall_feedback.get('communication_quality', 'N/A'),
                'suitability_score': overall_feedback.get('suitability_score', 0)
            }),
            assessment_id
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "completed",
            "message": "Assessment recomputed successfully",
            "overall_score": overall_feedback['overall_score'],
            "overall_score_percent": overall_feedback['overall_score_percent']
        }
        
    except Exception as e:
        conn.close()
        print(f"Error recomputing assessment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to recompute assessment: {str(e)}")

@app.delete("/api/assessments/{assessment_id}")
async def delete_assessment(assessment_id: int):
    """Delete an assessment and optionally the candidate"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get interview details
    interview = cursor.execute(
        "SELECT application_id FROM interview WHERE id = ?", (assessment_id,)
    ).fetchone()
    
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    try:
        # Delete transcript chunks for this interview
        cursor.execute("""
            DELETE FROM transcript_chunk 
            WHERE answer_id IN (
                SELECT id FROM answer WHERE interview_id = ?
            )
        """, (assessment_id,))
        
        # Delete answers
        cursor.execute("DELETE FROM answer WHERE interview_id = ?", (assessment_id,))
        
        # Delete questions
        cursor.execute("DELETE FROM question WHERE interview_id = ?", (assessment_id,))
        
        # Delete proctoring events
        cursor.execute("DELETE FROM proctor_event WHERE interview_id = ?", (assessment_id,))
        
        # Delete interview
        cursor.execute("DELETE FROM interview WHERE id = ?", (assessment_id,))
        
        # If there's an application, update its status
        if interview['application_id']:
            cursor.execute(
                "UPDATE applications SET status = 'qualified' WHERE id = ?",
                (interview['application_id'],)
            )
        
        conn.commit()
        conn.close()
        
        return {
            "status": "deleted",
            "message": "Assessment deleted successfully"
        }
        
    except Exception as e:
        conn.close()
        print(f"Error deleting assessment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete assessment: {str(e)}")

@app.post("/api/interviews")
async def create_interview(interview: InterviewCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    
    candidate_name = interview.candidate_name
    candidate_email = interview.candidate_email
    
    # If application_id is provided, get candidate info from application
    if interview.application_id:
        # Update application status to interviewed
        cursor.execute(
            "UPDATE applications SET status = 'interviewed' WHERE id = ?",
            (interview.application_id,)
        )
        
        # Get candidate info from application
        app_data = cursor.execute("""
            SELECT c.name, c.email 
            FROM applications a 
            JOIN candidates c ON a.candidate_id = c.id 
            WHERE a.id = ?
        """, (interview.application_id,)).fetchone()
        
        if app_data:
            candidate_name = app_data['name']
            candidate_email = app_data['email']
    
    cursor.execute(
        "INSERT INTO interview (candidate_name, candidate_email, started_at, status, application_id) VALUES (?, ?, ?, ?, ?)",
        (candidate_name, candidate_email, now, "in_progress", interview.application_id)
    )
    interview_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"interview_id": interview_id, "session_token": "dummy_token_123", "application_id": interview.application_id}

@app.get("/api/interviews/{interview_id}")
async def get_interview(interview_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    interview = cursor.execute("SELECT * FROM interview WHERE id = ?", (interview_id,)).fetchone()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Get questions with their answers
    questions_raw = cursor.execute("SELECT * FROM question WHERE interview_id = ? ORDER BY seq", (interview_id,)).fetchall()
    questions = []
    
    for q in questions_raw:
        q_dict = dict(q)
        # Get answer for this question
        answer = cursor.execute("SELECT * FROM answer WHERE question_id = ?", (q['id'],)).fetchone()
        q_dict['answer'] = dict(answer) if answer else None
        questions.append(q_dict)
    
    conn.close()
    return {
        **dict(interview),
        "questions": questions
    }

@app.post("/api/interviews/{interview_id}/answers/{answer_id}/evaluate")
async def evaluate_answer(interview_id: int, answer_id: int):
    """Evaluate a candidate's answer using AI"""
    from answer_evaluator import AnswerEvaluator
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get answer with question and transcript
    answer_data = cursor.execute("""
        SELECT 
            a.id as answer_id,
            q.text as question,
            q.id as question_id,
            a.interview_id
        FROM answer a
        JOIN question q ON a.question_id = q.id
        WHERE a.id = ? AND a.interview_id = ?
    """, (answer_id, interview_id)).fetchone()
    
    if not answer_data:
        conn.close()
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Get transcript for this answer
    transcripts = cursor.execute("""
        SELECT text FROM transcript_chunk 
        WHERE answer_id = ? AND is_final = 1
        ORDER BY timestamp
    """, (answer_id,)).fetchall()
    
    answer_text = ' '.join([t['text'] for t in transcripts])
    
    if not answer_text or len(answer_text) < 5:
        conn.close()
        return {
            "score": 0.0,
            "verdict": "No answer provided",
            "strengths": [],
            "weaknesses": ["No response recorded"]
        }
    
    # Evaluate using AI
    evaluator = AnswerEvaluator()
    evaluation = evaluator.evaluate_answer(
        question=answer_data['question'],
        answer_text=answer_text
    )
    
    # Store evaluation in database
    cursor.execute("""
        UPDATE answer 
        SET score = ?, verdict = ?, auto_score_breakdown = ?
        WHERE id = ?
    """, (
        evaluation['score'],
        evaluation['verdict'],
        json.dumps({
            'strengths': evaluation['strengths'],
            'weaknesses': evaluation['weaknesses']
        }),
        answer_id
    ))
    
    conn.commit()
    conn.close()
    
    return evaluation

@app.post("/api/interviews/{interview_id}/complete")
async def complete_interview(interview_id: int, background_tasks: BackgroundTasks):
    """Mark interview as completed and generate overall feedback"""
    from answer_evaluator import AnswerEvaluator
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all answers with questions and transcripts
    answers = cursor.execute("""
        SELECT 
            a.id as answer_id,
            a.score,
            a.verdict,
            q.text as question,
            q.seq
        FROM answer a
        JOIN question q ON a.question_id = q.id
        WHERE a.interview_id = ?
        ORDER BY q.seq
    """, (interview_id,)).fetchall()
    
    # Prepare data for overall feedback
    answers_data = []
    for ans in answers:
        # Get transcript for this answer
        transcripts = cursor.execute("""
            SELECT text FROM transcript_chunk 
            WHERE answer_id = ? AND is_final = 1
            ORDER BY timestamp
        """, (ans['answer_id'],)).fetchall()
        
        answer_text = ' '.join([t['text'] for t in transcripts])
        
        answers_data.append({
            'question': ans['question'],
            'answer_text': answer_text,
            'score': ans['score'] or 0.0,
            'verdict': ans['verdict'] or 'Not evaluated'
        })
    
    # Generate overall feedback
    evaluator = AnswerEvaluator()
    overall_feedback = evaluator.generate_overall_feedback(answers_data)
    
    # Update interview with feedback and scores
    cursor.execute("""
        UPDATE interview 
        SET status = 'completed', 
            ended_at = ?,
            total_score = ?,
            notes = ?
        WHERE id = ?
    """, (
        datetime.now(),
        overall_feedback['overall_score'],
        json.dumps({
            'overall_feedback': overall_feedback['overall_feedback'],
            'detailed_feedback': overall_feedback['detailed_feedback'],
            'overall_score_percent': overall_feedback['overall_score_percent']
        }),
        interview_id
    ))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found")
    
    conn.commit()
    conn.close()
    
    return {
        "status": "completed",
        "message": "Interview marked as completed",
        "overall_score": overall_feedback['overall_score'],
        "overall_score_percent": overall_feedback['overall_score_percent']
    }

@app.get("/api/interviews/{interview_id}/greeting")
async def get_interview_greeting(interview_id: int, language: str = "English"):
    """Generate personalized greeting for interview start"""
    from gemini_service import GeminiService
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get interview details with application and job info
    interview_data = cursor.execute("""
        SELECT 
            i.candidate_name,
            j.title as job_title
        FROM interview i
        LEFT JOIN applications a ON i.application_id = a.id
        LEFT JOIN jobs j ON a.job_id = j.id
        WHERE i.id = ?
    """, (interview_id,)).fetchone()
    
    conn.close()
    
    if not interview_data:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    candidate_name = interview_data['candidate_name'] or "Candidate"
    job_title = interview_data['job_title'] or "Telesales"
    
    gemini = GeminiService()
    greeting_text = gemini.generate_greeting(candidate_name, job_title, language)
    
    # Generate TTS audio for greeting
    audio_base64 = gemini.text_to_speech(greeting_text, language=language)
    
    return {
        "greeting": greeting_text,
        "audio": audio_base64,
        "candidate_name": candidate_name,
        "job_title": job_title
    }

@app.post("/api/interviews/{interview_id}/questions/generate")
async def generate_question(interview_id: int, params: QuestionGenerate):
    from gemini_service import GeminiService
    
    gemini = GeminiService()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current question count
    current_count = cursor.execute(
        "SELECT COUNT(*) FROM question WHERE interview_id = ?", 
        (interview_id,)
    ).fetchone()[0]
    
    question_number = current_count + 1
    
    # Get question counts from environment
    resume_count = int(os.getenv('RESUME_QUESTIONS_COUNT', 2))
    technical_count = int(os.getenv('TECHNICAL_QUESTIONS_COUNT', 2))
    hr_count = int(os.getenv('HR_QUESTIONS_COUNT', 1))
    total_questions = resume_count + technical_count + hr_count
    
    # Determine question type based on current count
    if question_number <= resume_count:
        question_type = "resume"
    elif question_number <= resume_count + technical_count:
        question_type = "technical"
    else:
        question_type = "hr"
    
    # Generate question using Gemini
    question_text = gemini.generate_question(
        difficulty=params.difficulty,
        language=params.language,
        job_role="Telesales",
        question_number=question_number,
        total_questions=total_questions,
        question_type=question_type
    )
    
    # Generate TTS audio with the selected language
    audio_base64 = gemini.text_to_speech(question_text, language=params.language)
    
    # Get next sequence number
    last_seq = cursor.execute(
        "SELECT MAX(seq) FROM question WHERE interview_id = ?", 
        (interview_id,)
    ).fetchone()[0]
    next_seq = (last_seq or 0) + 1
    
    cursor.execute(
        "INSERT INTO question (interview_id, seq, text, prompt_source, asked_at) VALUES (?, ?, ?, ?, ?)",
        (interview_id, next_seq, question_text, f"{question_type}_question", datetime.now())
    )
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "question": {
            "id": question_id, 
            "seq": next_seq, 
            "text": question_text,
            "audio": audio_base64,
            "question_number": question_number,
            "total_questions": total_questions,
            "question_type": question_type
        }
    }

@app.post("/api/interviews/{interview_id}/answers/{question_id}/upload")
async def upload_answer(
    interview_id: int, 
    question_id: int, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    start_time: str = Form(...),
    end_time: str = Form(...)
):
    # Save file
    filename = f"{interview_id}_{question_id}.webm"
    file_location = f"data/media/{filename}"
    cropped_location = f"data/media/cropped_{filename}"
    
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Trigger cropping task (background)
    from media_processor import crop_video_to_face
    background_tasks.add_task(crop_video_to_face, file_location, cropped_location)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if answer already exists (from transcript)
    existing_answer = cursor.execute(
        "SELECT id FROM answer WHERE question_id = ? AND interview_id = ?",
        (question_id, interview_id)
    ).fetchone()
    
    if existing_answer:
        # Update existing answer with video
        answer_id = existing_answer['id']
        cursor.execute(
            '''UPDATE answer 
               SET recording_path = ?, cropped_recording_path = ?, end_time = ?, duration_seconds = ?
               WHERE id = ?''',
            (file_location, cropped_location, end_time, 0, answer_id)
        )
    else:
        # Create new answer
        cursor.execute(
            '''INSERT INTO answer 
               (question_id, interview_id, recording_path, cropped_recording_path, start_time, end_time, duration_seconds) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (question_id, interview_id, file_location, cropped_location, start_time, end_time, 0) 
        )
        answer_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    # Trigger answer evaluation in background
    from answer_evaluator import AnswerEvaluator
    
    async def evaluate_answer_task():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get question and transcript
            question_data = cursor.execute(
                "SELECT text FROM question WHERE id = ?", (question_id,)
            ).fetchone()
            
            transcripts = cursor.execute("""
                SELECT text FROM transcript_chunk 
                WHERE answer_id = ? AND is_final = 1
                ORDER BY timestamp
            """, (answer_id,)).fetchall()
            
            answer_text = ' '.join([t['text'] for t in transcripts])
            
            if answer_text and len(answer_text) >= 5:
                evaluator = AnswerEvaluator()
                evaluation = evaluator.evaluate_answer(
                    question=question_data['text'],
                    answer_text=answer_text
                )
                
                # Store evaluation
                cursor.execute("""
                    UPDATE answer 
                    SET score = ?, verdict = ?, auto_score_breakdown = ?
                    WHERE id = ?
                """, (
                    evaluation['score'],
                    evaluation['verdict'],
                    json.dumps({
                        'strengths': evaluation['strengths'],
                        'weaknesses': evaluation['weaknesses']
                    }),
                    answer_id
                ))
                
                conn.commit()
                print(f"Answer {answer_id} evaluated: {evaluation['score']}/5")
            
            conn.close()
        except Exception as e:
            print(f"Error in answer evaluation task: {e}")
            import traceback
            traceback.print_exc()
    
    background_tasks.add_task(evaluate_answer_task)
    
    return {"answer_id": answer_id}

@app.post("/api/interviews/{interview_id}/transcript")
async def save_transcript_chunk(interview_id: int, chunk: TranscriptChunk):
    """Save transcript chunk to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the current question being answered
    current_question = cursor.execute(
        "SELECT id FROM question WHERE interview_id = ? ORDER BY seq DESC LIMIT 1",
        (interview_id,)
    ).fetchone()
    
    if not current_question:
        conn.close()
        raise HTTPException(status_code=404, detail="No active question found")
    
    question_id = current_question['id']
    
    # Get or create answer for this question
    answer = cursor.execute(
        "SELECT id FROM answer WHERE question_id = ? AND interview_id = ?",
        (question_id, interview_id)
    ).fetchone()
    
    if not answer:
        # Create a placeholder answer if it doesn't exist yet
        cursor.execute(
            '''INSERT INTO answer (question_id, interview_id, start_time) 
               VALUES (?, ?, ?)''',
            (question_id, interview_id, datetime.now())
        )
        answer_id = cursor.lastrowid
    else:
        answer_id = answer['id']
    
    # Save transcript chunk
    cursor.execute(
        '''INSERT INTO transcript_chunk (answer_id, timestamp, text, is_final)
           VALUES (?, ?, ?, ?)''',
        (answer_id, chunk.timestamp, chunk.text, chunk.is_final)
    )
    
    conn.commit()
    conn.close()
    
    return {"status": "ok", "answer_id": answer_id}

@app.post("/api/interviews/{interview_id}/proctor/event")
async def log_proctor_event(interview_id: int, event: ProctorEvent):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    frame_path = ""
    server_analysis_notes = ""
    
    if event.frame_base64:
        # Save frame
        try:
            frame_data = base64.b64decode(event.frame_base64.split(",")[1])
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            frame_path = f"data/frames/{interview_id}_{event.event_type}_{timestamp_str}.jpg"
            with open(frame_path, "wb") as f:
                f.write(frame_data)
            
            # Run Server-side verification
            from proctoring import ProctorEngine
            engine = ProctorEngine()
            server_events = engine.analyze_frame(frame_path)
            if server_events:
                server_analysis_notes = f" [Server Verified: {', '.join([e['type'] for e in server_events])}]"
        except Exception as e:
            print(f"Frame processing error: {e}")
            
    cursor.execute(
        '''INSERT INTO proctor_event 
           (interview_id, event_type, confidence, frame_path, notes, timestamp) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (interview_id, event.event_type, event.confidence, frame_path, (event.notes or "") + server_analysis_notes, datetime.now())
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/interviews/recent")
async def get_recent_interviews():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get interviews with question count
    interviews = cursor.execute("""
        SELECT i.*, COUNT(q.id) as question_count
        FROM interview i
        LEFT JOIN question q ON i.id = q.interview_id
        GROUP BY i.id
        ORDER BY i.started_at DESC
        LIMIT 50
    """).fetchall()
    
    conn.close()
    
    return {
        "interviews": [dict(i) for i in interviews]
    }

@app.get("/api/dashboard/interviews")
async def list_interviews():
    conn = get_db_connection()
    cursor = conn.cursor()
    interviews = cursor.execute("SELECT * FROM interview ORDER BY started_at DESC").fetchall()
    conn.close()
    return [dict(i) for i in interviews]

# --- WebSocket ---
@app.websocket("/ws/interview/{interview_id}")
async def websocket_endpoint(websocket: WebSocket, interview_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received WS message: {data}")
            
            try:
                msg = json.loads(data)
                
                # Handle transcript chunks from client
                if msg.get('type') == 'transcript_chunk':
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Get the current question being answered
                    current_question = cursor.execute(
                        "SELECT id FROM question WHERE interview_id = ? ORDER BY seq DESC LIMIT 1",
                        (interview_id,)
                    ).fetchone()
                    
                    if current_question:
                        question_id = current_question['id']
                        
                        # Get or create answer for this question
                        answer = cursor.execute(
                            "SELECT id FROM answer WHERE question_id = ? AND interview_id = ?",
                            (question_id, interview_id)
                        ).fetchone()
                        
                        if not answer:
                            # Create a placeholder answer if it doesn't exist yet
                            cursor.execute(
                                '''INSERT INTO answer (question_id, interview_id, start_time) 
                                   VALUES (?, ?, ?)''',
                                (question_id, interview_id, datetime.now())
                            )
                            answer_id = cursor.lastrowid
                        else:
                            answer_id = answer['id']
                        
                        # Save transcript chunk
                        cursor.execute(
                            '''INSERT INTO transcript_chunk (answer_id, timestamp, text, is_final)
                               VALUES (?, ?, ?, ?)''',
                            (answer_id, msg.get('timestamp'), msg.get('text'), msg.get('is_final', False))
                        )
                        
                        conn.commit()
                        print(f"Saved transcript chunk for answer {answer_id}: {msg.get('text')}")
                    
                    conn.close()
                    
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {data}")
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")
                import traceback
                traceback.print_exc()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
