import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Mail, Phone, Briefcase, Calendar } from 'lucide-react';
import './AssessmentReport.css';

const AssessmentReport = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [assessment, setAssessment] = useState(null);
    const [activeTab, setActiveTab] = useState('score');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAssessmentDetails();
    }, [id]);

    const fetchAssessmentDetails = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/assessments/${id}`);
            if (res.ok) {
                const data = await res.json();
                setAssessment(data);
            }
            setLoading(false);
        } catch (err) {
            console.error('Error fetching assessment:', err);
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading-page">Loading assessment...</div>;
    }

    if (!assessment) {
        return <div className="error-page">Assessment not found</div>;
    }

    const overallPercent = assessment.overallScorePercent || 0;
    const overallScore = assessment.overallScore || 0;
    const maxScore = assessment.maxScore || 5.0;

    const metrics = assessment.metrics || { good: 0, average: 0, below: 0, warnings: 0 };
    const topicBreakdown = assessment.topicBreakdown || [];

    const feedback = assessment.feedback || {
        aiOverall: "Assessment feedback not yet generated.",
        detailed: "Detailed feedback not yet generated."
    };

    const answers = assessment.answers || [];

    const getScoreColor = (score, max) => {
        const percent = (score / max) * 100;
        if (percent >= 80) return '#10B981';
        if (percent >= 50) return '#F59E0B';
        return '#EF4444';
    };

    return (
        <div className="assessment-report">
            <div className="report-header">
                <button className="btn-back" onClick={() => navigate('/dashboard')}>
                    <ArrowLeft size={20} />
                    Back to Assessments
                </button>
                <h1>Candidate Assessment Report</h1>
            </div>

            <div className="report-content">
                {/* Candidate Info & Score */}
                <div className="candidate-section">
                    <div className="candidate-profile">
                        <div className="profile-avatar">
                            <User size={48} />
                        </div>
                        <div className="profile-info">
                            <h2>{assessment.candidate?.name || 'Unknown'}</h2>
                            <div className="info-grid">
                                <div className="info-item">
                                    <Briefcase size={16} />
                                    <span>Position: {assessment.candidate?.position || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <Mail size={16} />
                                    <span>Email: {assessment.candidate?.email || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <Phone size={16} />
                                    <span>Phone: {assessment.candidate?.phone || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <Calendar size={16} />
                                    <span>Assessment ID: #{assessment.id}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="score-doughnut">
                        <h3>Overall Score</h3>
                        <div className="doughnut-chart">
                            <svg viewBox="0 0 200 200" className="doughnut-svg">
                                <circle
                                    cx="100"
                                    cy="100"
                                    r="80"
                                    fill="none"
                                    stroke="#E5E7EB"
                                    strokeWidth="20"
                                />
                                <circle
                                    cx="100"
                                    cy="100"
                                    r="80"
                                    fill="none"
                                    stroke="#10B981"
                                    strokeWidth="20"
                                    strokeDasharray={`${(overallPercent / 100) * 502.4} 502.4`}
                                    strokeLinecap="round"
                                    transform="rotate(-90 100 100)"
                                />
                            </svg>
                            <div className="doughnut-center">
                                {/* <div className="score-percent">{overallPercent}%</div> */}
                                <div className="score-fraction">{overallScore}/{maxScore}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Performance Metrics */}
                <div className="metrics-row">
                    <div className="metric-card good">
                        <h3>{metrics.good}</h3>
                        <p>Good Performance</p>
                        <span>Questions (80-100%)</span>
                    </div>
                    <div className="metric-card average">
                        <h3>{metrics.average}</h3>
                        <p>Average Performance</p>
                        <span>Questions (40-79%)</span>
                    </div>
                    <div className="metric-card below">
                        <h3>{metrics.below}</h3>
                        <p>Below Average</p>
                        <span>Questions (0-40%)</span>
                    </div>
                    <div className="metric-card warnings">
                        <h3>{metrics.warnings}</h3>
                        <p>Total Warnings</p>
                        <span>Proctoring Alerts</span>
                    </div>
                </div>

                {/* Tabs */}
                <div className="tabs-container">
                    <div className="tabs-header">
                        <button
                            className={`tab ${activeTab === 'score' ? 'active' : ''}`}
                            onClick={() => setActiveTab('score')}
                        >
                            📊 Score
                        </button>
                        <button
                            className={`tab ${activeTab === 'overall' ? 'active' : ''}`}
                            onClick={() => setActiveTab('overall')}
                        >
                            📝 Overall Feedback
                        </button>
                        <button
                            className={`tab ${activeTab === 'detailed' ? 'active' : ''}`}
                            onClick={() => setActiveTab('detailed')}
                        >
                            📋 Detailed Feedback
                        </button>
                        <button
                            className={`tab ${activeTab === 'transcript' ? 'active' : ''}`}
                            onClick={() => setActiveTab('transcript')}
                        >
                            🎥 Transcript ({answers.length || 17})
                        </button>
                    </div>

                    <div className="tab-content">
                        {activeTab === 'score' && (
                            <div className="score-tab">
                                <div className="section-header">
                                    <h2>Topic Wise Score</h2>
                                    <span className="sort-label">Sort By: Score (High to Low)</span>
                                </div>
                                <div className="topic-bars">
                                    {topicBreakdown.map((topic, idx) => (
                                        <div key={idx} className="topic-bar-item">
                                            <div className="topic-label">{topic.topic}</div>
                                            <div className="topic-bar-container">
                                                <div
                                                    className="topic-bar-fill"
                                                    style={{
                                                        width: `${(topic.score / topic.max) * 100}%`,
                                                        background: getScoreColor(topic.score, topic.max)
                                                    }}
                                                />
                                            </div>
                                            <div className="topic-score">{topic.score}/{topic.max}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'overall' && (
                            <div className="feedback-tab">
                                <h2>AI-Generated Overall Assessment</h2>
                                <div className="feedback-section">
                                    <h3>Comprehensive Feedback:</h3>
                                    <p className="feedback-text">{feedback.aiOverall}</p>

                                    <div className="suitability-score">
                                        <h3>Suitability Score: {feedback.suitabilityScore || overallPercent}/100</h3>
                                        <div className="suitability-bar">
                                            <div className="suitability-fill" style={{ width: `${feedback.suitabilityScore || overallPercent}%` }}>
                                                <span>{(feedback.suitabilityScore || overallPercent).toFixed(0)}%</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'detailed' && (
                            <div className="detailed-tab">
                                <div className="detailed-notice">
                                    ℹ️ This detailed analysis is AI-generated based on the candidate's responses, confidence, technical knowledge, and communication skills.
                                </div>

                                <div className="detailed-content">
                                    <h3>📋 Comprehensive Assessment:</h3>
                                    <p className="detailed-text">{feedback.detailed}</p>

                                    {topicBreakdown.length > 0 && (
                                        <>
                                            <h3>💡 Technical Strength by Domain:</h3>
                                            <ul className="strength-list">
                                                {topicBreakdown.map((topic, idx) => (
                                                    <li key={idx}>
                                                        <strong>{topic.topic}:</strong> {topic.score >= 4 ? 'Strong' : topic.score >= 3 ? 'Good' : 'Needs Improvement'} 
                                                        <span className={`score-tag ${topic.score < 3 ? 'low' : ''}`}>
                                                            {topic.score.toFixed(1)}/{topic.max}
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </>
                                    )}

                                    <h3>🔍 Key Observations:</h3>
                                    <ul className="observations-list">
                                        {feedback.confidenceLevel && (
                                            <li><strong>Confidence Level:</strong> {feedback.confidenceLevel}</li>
                                        )}
                                        {feedback.communicationQuality && (
                                            <li><strong>Communication:</strong> {feedback.communicationQuality}</li>
                                        )}
                                        {feedback.keyStrengths && feedback.keyStrengths.map((strength, idx) => (
                                            <li key={idx}><strong>Strength:</strong> {strength}</li>
                                        ))}
                                        {feedback.areasForImprovement && feedback.areasForImprovement.map((area, idx) => (
                                            <li key={idx}><strong>Area for Improvement:</strong> {area}</li>
                                        ))}
                                    </ul>

                                    <div className="overall-suitability">
                                        <h3>Overall Suitability: {feedback.suitabilityScore || overallPercent}/100</h3>
                                        <div className="suitability-bar-full">
                                            <div className="suitability-fill-full" style={{ width: `${feedback.suitabilityScore || overallPercent}%` }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'transcript' && (
                            <div className="transcript-tab">
                                <h2>Interview Transcript with Recordings</h2>
                                {answers.length === 0 ? (
                                    <div className="empty-state">No answers recorded yet</div>
                                ) : (
                                    <div className="transcript-list">
                                        {answers.map((answer, idx) => (
                                            <div key={answer.id} className="transcript-item">
                                                <div className="question-header">
                                                    <span className="q-number">Q{idx + 1}</span>
                                                    <span className="q-type">{answer.scorePercent >= 80 ? 'GOOD' : answer.scorePercent >= 40 ? 'AVERAGE' : 'BELOW'}</span>
                                                    <span className="q-score">Score: {answer.score.toFixed(1)}/5</span>
                                                </div>
                                                <p className="question-text">
                                                    <strong>Question:</strong> {answer.question}
                                                </p>
                                                
                                                <div className="answer-section">
                                                    <div className="answer-header-label">
                                                        <strong>Candidate's Answer:</strong>
                                                    </div>
                                                    {answer.transcriptSegments && answer.transcriptSegments.length > 0 ? (
                                                        <div className="answer-transcript">
                                                            {answer.transcriptSegments.map((segment, segIdx) => (
                                                                <span key={segIdx} className={segment.is_final ? 'transcript-final' : 'transcript-interim'}>
                                                                    {segment.text}{' '}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <p className="no-transcript">No transcript available for this answer</p>
                                                    )}
                                                </div>

                                                {answer.verdict && (
                                                    <div className="verdict-section">
                                                        <strong>AI Verdict:</strong>
                                                        <p className="verdict-text">{answer.verdict}</p>
                                                    </div>
                                                )}
                                                {answer.mediaId ? (
                                                    <div className="video-container">
                                                        <video controls className="answer-video">
                                                            <source src={`http://localhost:8000/${answer.mediaId}`} type="video/webm" />
                                                            Your browser does not support video playback.
                                                        </video>
                                                        <div className="answer-meta">
                                                            <span>📹 Video Recording</span>
                                                            <div className="score-bar">
                                                                <div 
                                                                    className="score-fill" 
                                                                    style={{ 
                                                                        width: `${answer.scorePercent}%`, 
                                                                        background: getScoreColor(answer.score, 5) 
                                                                    }} 
                                                                />
                                                                <span className="score-percent">{answer.scorePercent.toFixed(0)}%</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="answer-meta">
                                                        <span>No video recording</span>
                                                        <div className="score-bar">
                                                            <div 
                                                                className="score-fill" 
                                                                style={{ 
                                                                    width: `${answer.scorePercent}%`, 
                                                                    background: getScoreColor(answer.score, 5) 
                                                                }} 
                                                            />
                                                            <span className="score-percent">{answer.scorePercent.toFixed(0)}%</span>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssessmentReport;
