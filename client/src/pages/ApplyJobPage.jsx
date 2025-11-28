import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Upload, FileText, ArrowLeft } from 'lucide-react';
import './ApplyJobPage.css';

const ApplyJobPage = () => {
    const { jobId } = useParams();
    const navigate = useNavigate();
    const [job, setJob] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        resume: null
    });
    const [fileName, setFileName] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchJob();
    }, [jobId]);

    const fetchJob = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`);
            if (!response.ok) throw new Error('Job not found');
            const data = await response.json();
            setJob(data);
        } catch (error) {
            console.error('Error fetching job:', error);
            setError('Job not found');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
            if (!allowedTypes.includes(file.type)) {
                setError('Only PDF and DOCX files are accepted');
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                setError('File size must be less than 10MB');
                return;
            }
            setFormData({ ...formData, resume: file });
            setFileName(file.name);
            setError('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.name || !formData.email || !formData.resume) {
            setError('Please fill all fields and upload your resume');
            return;
        }

        setSubmitting(true);

        try {
            const submitData = new FormData();
            submitData.append('job_id', jobId);
            submitData.append('name', formData.name);
            submitData.append('email', formData.email);
            submitData.append('file', formData.resume);

            const response = await fetch('http://localhost:8000/api/applications', {
                method: 'POST',
                body: submitData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to submit application');
            }

            const result = await response.json();
            
            // Navigate to match result page
            navigate(`/applications/${result.application_id}/result`, {
                state: { result, job }
            });

        } catch (error) {
            console.error('Error submitting application:', error);
            setError(error.message || 'Failed to submit application. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="apply-job-container">
                <div className="loading">Loading...</div>
            </div>
        );
    }

    if (error && !job) {
        return (
            <div className="apply-job-container">
                <div className="error-page">
                    <h2>Job Not Found</h2>
                    <button onClick={() => navigate('/')}>Back to Jobs</button>
                </div>
            </div>
        );
    }

    return (
        <div className="apply-job-container">
            <header className="apply-header">
                <div className="logo">
                    <div className="logo-icon"></div>
                    <span>matrimony.com</span>
                </div>
                <button className="back-button" onClick={() => navigate('/')}>
                    <ArrowLeft size={20} />
                    Back to Jobs
                </button>
            </header>

            <div className="apply-content">
                <div className="apply-form-section">
                    <h1>Apply for {job?.title}</h1>
                    <p className="subtitle">Upload your resume to check your match and start the AI assessment.</p>

                    <form onSubmit={handleSubmit} className="application-form">
                        <div className="form-group">
                            <label>Full Name *</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="Enter your full name"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Email *</label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                placeholder="your.email@example.com"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Resume (PDF/DOCX) *</label>
                            <div className="file-upload-area">
                                <input
                                    type="file"
                                    id="resume-upload"
                                    accept=".pdf,.docx,.doc"
                                    onChange={handleFileChange}
                                    style={{ display: 'none' }}
                                />
                                <label htmlFor="resume-upload" className="file-upload-label">
                                    {fileName ? (
                                        <>
                                            <FileText size={24} />
                                            <span>{fileName}</span>
                                        </>
                                    ) : (
                                        <>
                                            <Upload size={24} />
                                            <span>Choose File</span>
                                            <span className="file-hint">PDF or DOCX, max 10MB</span>
                                        </>
                                    )}
                                </label>
                            </div>
                        </div>

                        {error && (
                            <div className="error-message">
                                {error}
                            </div>
                        )}

                        <button 
                            type="submit" 
                            className="submit-button"
                            disabled={submitting}
                        >
                            {submitting ? 'Processing...' : 'Upload & Check Match'}
                        </button>
                    </form>
                </div>

                <div className="job-description-section">
                    <h2>Job Description</h2>
                    <div className="job-meta">
                        <span><strong>Location:</strong> {job?.location}</span>
                        <span><strong>Type:</strong> {job?.job_type}</span>
                        <span><strong>Experience:</strong> {job?.experience_required}</span>
                    </div>
                    <div className="job-description-text">
                        <pre>{job?.description}</pre>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ApplyJobPage;
