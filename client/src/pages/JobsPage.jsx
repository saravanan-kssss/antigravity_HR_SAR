import React, { useState, useEffect } from 'react';
import { Plus, Briefcase, MapPin, Users, Edit, Trash2, Upload, FileText } from 'lucide-react';
import CreateJobModal from '../components/CreateJobModal';
import './JobsPage.css';

const JobsPage = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [createMode, setCreateMode] = useState(null); // 'upload' or 'manual'

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/jobs?active_only=false');
            const data = await response.json();
            setJobs(data.jobs);
        } catch (error) {
            console.error('Error fetching jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateClick = (mode) => {
        setCreateMode(mode);
        setShowCreateModal(true);
    };

    const handleJobCreated = () => {
        setShowCreateModal(false);
        setCreateMode(null);
        fetchJobs();
    };

    const handleToggleActive = async (jobId, currentStatus) => {
        const newStatus = !currentStatus;
        const action = newStatus ? 'activate' : 'deactivate';
        
        if (!window.confirm(`Are you sure you want to ${action} this job?`)) return;

        try {
            await fetch(`http://localhost:8000/api/jobs/${jobId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_active: newStatus })
            });
            fetchJobs();
        } catch (error) {
            console.error('Error updating job status:', error);
            alert('Failed to update job status');
        }
    };

    const handleDeleteJob = async (jobId) => {
        const choice = window.confirm(
            'Choose deletion type:\n\n' +
            'OK = Permanent Delete (cannot be undone)\n' +
            'Cancel = Mark as Inactive (can be reactivated later)'
        );

        if (choice === null) return; // User cancelled

        const permanent = choice === true;

        try {
            const url = permanent 
                ? `http://localhost:8000/api/jobs/${jobId}?permanent=true`
                : `http://localhost:8000/api/jobs/${jobId}`;
                
            const response = await fetch(url, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || 'Failed to delete job');
                return;
            }

            fetchJobs();
        } catch (error) {
            console.error('Error deleting job:', error);
            alert('Failed to delete job');
        }
    };

    if (loading) {
        return (
            <div className="jobs-page">
                <div className="loading">Loading jobs...</div>
            </div>
        );
    }

    return (
        <div className="jobs-page">
            <div className="page-header">
                <div>
                    <h1>Jobs Management</h1>
                    <p>Create and manage job postings</p>
                </div>
                <button className="btn-create-job" onClick={() => setShowCreateModal(true)}>
                    <Plus size={20} />
                    Create Job
                </button>
            </div>

            {!createMode && showCreateModal && (
                <div className="create-mode-selector">
                    <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                        <div className="mode-selector-content" onClick={(e) => e.stopPropagation()}>
                            <h2>Create Job</h2>
                            <p>Choose how you want to create the job posting</p>
                            
                            <div className="mode-options">
                                <div className="mode-card" onClick={() => handleCreateClick('upload')}>
                                    <Upload size={48} />
                                    <h3>Upload JD</h3>
                                    <p>PDF / DOC / DOCX / TXT / MD</p>
                                    <button className="btn-mode">Choose File</button>
                                </div>

                                <div className="mode-card" onClick={() => handleCreateClick('manual')}>
                                    <FileText size={48} />
                                    <h3>Manual Entry</h3>
                                    <p>Fill the job details manually</p>
                                    <button className="btn-mode">Start</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {createMode && showCreateModal && (
                <CreateJobModal
                    mode={createMode}
                    onClose={() => {
                        setShowCreateModal(false);
                        setCreateMode(null);
                    }}
                    onJobCreated={handleJobCreated}
                />
            )}

            <div className="jobs-stats">
                <div className="stat-card">
                    <Briefcase size={24} />
                    <div>
                        <div className="stat-value">{jobs.filter(j => j.is_active).length}</div>
                        <div className="stat-label">Active Jobs</div>
                    </div>
                </div>
                <div className="stat-card">
                    <Users size={24} />
                    <div>
                        <div className="stat-value">{jobs.reduce((sum, j) => sum + j.applicant_count, 0)}</div>
                        <div className="stat-label">Total Applicants</div>
                    </div>
                </div>
            </div>

            <div className="jobs-list">
                {jobs.length === 0 ? (
                    <div className="empty-state">
                        <Briefcase size={64} />
                        <h3>No jobs yet</h3>
                        <p>Create your first job posting to get started</p>
                        <button className="btn-create-job" onClick={() => setShowCreateModal(true)}>
                            <Plus size={20} />
                            Create Job
                        </button>
                    </div>
                ) : (
                    jobs.map(job => (
                        <div key={job.id} className={`job-item ${!job.is_active ? 'inactive' : ''}`}>
                            <div className="job-item-header">
                                <div>
                                    <h3>{job.title}</h3>
                                    {!job.is_active && <span className="inactive-badge">Inactive</span>}
                                </div>
                                <div className="job-actions">
                                    <button 
                                        className={`btn-toggle ${job.is_active ? 'active' : 'inactive'}`}
                                        onClick={() => handleToggleActive(job.id, job.is_active)}
                                        title={job.is_active ? 'Mark as Inactive' : 'Mark as Active'}
                                    >
                                        {job.is_active ? 'Active' : 'Inactive'}
                                    </button>
                                    <button className="btn-icon" title="Edit">
                                        <Edit size={18} />
                                    </button>
                                    <button className="btn-icon btn-danger" onClick={() => handleDeleteJob(job.id)} title="Delete">
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="job-item-details">
                                <div className="job-detail">
                                    <MapPin size={16} />
                                    <span>{job.location}</span>
                                </div>
                                <div className="job-detail">
                                    <Briefcase size={16} />
                                    <span>{job.job_type}</span>
                                </div>
                                <div className="job-detail">
                                    <Users size={16} />
                                    <span>{job.applicant_count} applicants</span>
                                </div>
                            </div>

                            <div className="job-description-preview">
                                {job.description.substring(0, 200)}...
                            </div>

                            <div className="job-meta">
                                <span>Experience: {job.experience_required}</span>
                                <span>Created: {new Date(job.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default JobsPage;
