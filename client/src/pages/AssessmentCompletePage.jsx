import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import './AssessmentCompletePage.css';

const AssessmentCompletePage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { interviewId } = location.state || {};

    const handleBackToJobs = () => {
        navigate('/');
    };

    const handleRefresh = () => {
        window.location.reload();
    };

    return (
        <div className="assessment-complete-container">
            <div className="assessment-complete-card">
                <h1 className="assessment-title">Assessment Result</h1>
                
                <div className="assessment-info">
                    <p><strong>Assessment ID:</strong> #{interviewId || '166'}</p>
                    <p><strong>Status:</strong> completed</p>
                </div>

                <div className="completion-message">
                    <div className="completion-icon">
                        <CheckCircle size={24} color="#10b981" />
                    </div>
                    <h2>Assessment Completed</h2>
                    <p className="completion-text">
                        Thank you for your time and effort. Our team will review your responses 
                        and contact you soon with the next steps.
                    </p>
                    <p className="completion-subtext">
                        Your assessment has been submitted successfully. We appreciate your participation.
                    </p>
                </div>

                <div className="action-buttons">
                    <button className="btn-refresh" onClick={handleRefresh}>
                        Refresh
                    </button>
                    <button className="btn-back-to-jobs" onClick={handleBackToJobs}>
                        Back to Jobs
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AssessmentCompletePage;
