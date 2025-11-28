import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { CheckCircle, XCircle, ArrowLeft, PlayCircle } from 'lucide-react';
import './MatchResultPage.css';

const MatchResultPage = () => {
    const { applicationId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [result, setResult] = useState(location.state?.result || null);
    const [job, setJob] = useState(location.state?.job || null);
    const [loading, setLoading] = useState(!result);

    useEffect(() => {
        if (!result) {
            fetchMatchResult();
        }
    }, [applicationId]);

    const fetchMatchResult = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/applications/${applicationId}/match-result`);
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Error fetching match result:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStartAssessment = () => {
        // Navigate to device check page with application context
        navigate('/interview', {
            state: {
                applicationId: applicationId,
                candidateName: result.candidate_name || 'Candidate',
                candidateEmail: result.candidate_email || '',
                jobTitle: result.job_title || 'Telesales'
            }
        });
    };

    const handleBackToJobs = () => {
        navigate('/');
    };

    if (loading) {
        return (
            <div className="match-result-container">
                <div className="loading">Loading results...</div>
            </div>
        );
    }

    const isQualified = result?.match_score >= 50;
    const scoreColor = result?.match_score >= 80 ? '#10b981' : 
                       result?.match_score >= 60 ? '#3b82f6' :
                       result?.match_score >= 50 ? '#f59e0b' : '#ef4444';

    return (
        <div className="match-result-container">
            <header className="result-header">
                <div className="logo">
                    <div className="logo-icon"></div>
                    <span>matrimony.com</span>
                </div>
                <p className="tagline">Connecting People, Empowering Hiring</p>
            </header>

            <div className="result-content">
                <div className="result-card">
                    <h1>Match Result</h1>

                    <div className="score-section">
                        <div className="score-circle" style={{ borderColor: scoreColor }}>
                            <div className="score-value" style={{ color: scoreColor }}>
                                {result?.match_score?.toFixed(1)}%
                            </div>
                            <div className="score-label">Match Score</div>
                        </div>
                    </div>

                    <div className="explanation-section">
                        <h2>Explanation:</h2>
                        <p className="explanation-text">{result?.match_explanation}</p>
                    </div>

                    {result?.strengths && result.strengths.length > 0 && (
                        <div className="strengths-section">
                            <h3>Strengths:</h3>
                            <ul>
                                {result.strengths.map((strength, index) => (
                                    <li key={index}>{strength}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {result?.gaps && result.gaps.length > 0 && (
                        <div className="gaps-section">
                            <h3>Areas for Improvement:</h3>
                            <ul>
                                {result.gaps.map((gap, index) => (
                                    <li key={index}>{gap}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {isQualified ? (
                        <div className="success-message">
                            <CheckCircle size={24} />
                            <p>✓ Congratulations! You meet the required criteria. You can now proceed to the AI Assessment.</p>
                        </div>
                    ) : (
                        <div className="rejection-message">
                            <XCircle size={24} />
                            <p>Unfortunately, your qualifications do not meet the minimum requirements for this position at this time.</p>
                        </div>
                    )}

                    <div className="action-buttons">
                        {isQualified ? (
                            <>
                                <button className="btn-secondary" onClick={handleBackToJobs}>
                                    <ArrowLeft size={20} />
                                    Back to Jobs
                                </button>
                                <button className="btn-primary" onClick={handleStartAssessment}>
                                    <PlayCircle size={20} />
                                    Start AI Assessment
                                </button>
                            </>
                        ) : (
                            <button className="btn-primary" onClick={handleBackToJobs}>
                                <ArrowLeft size={20} />
                                Back to Jobs
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MatchResultPage;
