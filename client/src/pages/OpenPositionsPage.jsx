import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, MapPin, Clock, ChevronRight } from 'lucide-react';
import './OpenPositionsPage.css';

const OpenPositionsPage = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedJob, setSelectedJob] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/jobs?active_only=true');
            const data = await response.json();
            setJobs(data.jobs);
        } catch (error) {
            console.error('Error fetching jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleViewJD = (job) => {
        setSelectedJob(job);
        setShowModal(true);
    };

    const handleApply = (jobId) => {
        navigate(`/jobs/${jobId}/apply`);
    };

    if (loading) {
        return (
            <div className="open-positions-container">
                <div className="loading">Loading positions...</div>
            </div>
        );
    }

    return (
        <div className="open-positions-container">
            <header className="positions-header">
                <div className="logo">
                    <div className="logo-icon"></div>
                    <span>matrimony.com</span>
                </div>
                <p className="tagline">Connecting People, Empowering Hiring</p>
            </header>

            <div className="positions-content">
                <div className="positions-title">
                    <h1>Open Positions</h1>
                    <p>Find your next opportunity with us</p>
                </div>

                <div className="jobs-grid">
                    {jobs.length === 0 ? (
                        <div className="no-jobs">
                            <p>No open positions available at the moment.</p>
                            <p>Please check back later!</p>
                        </div>
                    ) : (
                        jobs.map(job => (
                            <div key={job.id} className="job-card">
                                <div className="job-header">
                                    <h3>{job.title}</h3>
                                    <span className="job-type-badge">{job.job_type}</span>
                                </div>

                                <div className="job-details">
                                    <div className="job-detail-item">
                                        <MapPin size={16} />
                                        <span>{job.location}</span>
                                    </div>
                                    <div className="job-detail-item">
                                        <Clock size={16} />
                                        <span>{job.experience_required}</span>
                                    </div>
                                    <div className="job-detail-item">
                                        <Briefcase size={16} />
                                        <span>{job.applicant_count} applicants</span>
                                    </div>
                                </div>

                                <div className="job-description-preview">
                                    {job.description.substring(0, 150)}...
                                </div>

                                <div className="job-actions">
                                    <button 
                                        className="btn-view-jd"
                                        onClick={() => handleViewJD(job)}
                                    >
                                        View JD
                                    </button>
                                    <button 
                                        className="btn-apply"
                                        onClick={() => handleApply(job.id)}
                                    >
                                        Apply <ChevronRight size={16} />
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Job Description Modal */}
            {showModal && selectedJob && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{selectedJob.title}</h2>
                            <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
                        </div>
                        <div className="modal-body">
                            <div className="job-meta">
                                <span><MapPin size={16} /> {selectedJob.location}</span>
                                <span><Clock size={16} /> {selectedJob.experience_required}</span>
                                <span className="job-type-badge">{selectedJob.job_type}</span>
                            </div>
                            <div className="job-description-full">
                                <h3>Job Description</h3>
                                <pre>{selectedJob.description}</pre>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn-secondary" onClick={() => setShowModal(false)}>
                                Close
                            </button>
                            <button 
                                className="btn-primary" 
                                onClick={() => {
                                    setShowModal(false);
                                    handleApply(selectedJob.id);
                                }}
                            >
                                Apply Now
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default OpenPositionsPage;
