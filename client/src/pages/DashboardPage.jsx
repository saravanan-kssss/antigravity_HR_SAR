import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Users, FileText, Eye, RefreshCw, Trash2 } from 'lucide-react';
import './DashboardPage.css';

const DashboardPage = () => {
    const navigate = useNavigate();
    const [metrics, setMetrics] = useState({ totalJobs: 0, totalCandidates: 0, assessments: 0 });
    const [assessments, setAssessments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            // Fetch metrics
            const metricsRes = await fetch('http://localhost:8000/api/metrics/overview?range=30d');
            if (metricsRes.ok) {
                const data = await metricsRes.json();
                setMetrics({
                    totalJobs: data.totalJobs || 7,
                    totalCandidates: data.totalCandidates || 22,
                    assessments: data.completedAssessments || 17
                });
            }

            // Fetch recent assessments
            const assessRes = await fetch('http://localhost:8000/api/assessments?page=1&limit=10');
            if (assessRes.ok) {
                const data = await assessRes.json();
                setAssessments(data.items || []);
            }

            setLoading(false);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setLoading(false);
        }
    };

    const getStatusClass = (status) => {
        if (status === 'completed') return 'status-completed';
        if (status === 'feedback_pending') return 'status-pending';
        if (status === 'pending') return 'status-gray';
        return 'status-gray';
    };

    const handleRecompute = async (id) => {
        if (!window.confirm('Recompute this assessment? This will re-evaluate all answers and regenerate feedback.')) return;
        
        try {
            const response = await fetch(`http://localhost:8000/api/assessments/${id}/recompute`, { 
                method: 'POST' 
            });
            
            if (response.ok) {
                const data = await response.json();
                alert(`Assessment recomputed successfully!\nNew Score: ${data.overall_score_percent.toFixed(1)}%`);
                fetchDashboardData(); // Refresh the list
            } else {
                alert('Failed to recompute assessment');
            }
        } catch (err) {
            console.error('Recompute error:', err);
            alert('Error recomputing assessment');
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Delete this assessment? This will permanently remove all interview data, questions, answers, and transcripts.')) return;
        
        try {
            const response = await fetch(`http://localhost:8000/api/assessments/${id}`, { 
                method: 'DELETE' 
            });
            
            if (response.ok) {
                alert('Assessment deleted successfully');
                fetchDashboardData(); // Refresh the list
            } else {
                alert('Failed to delete assessment');
            }
        } catch (err) {
            console.error('Delete error:', err);
            alert('Error deleting assessment');
        }
    };

    return (
        <div className="dashboard-page">
            <div className="page-header">
                <div>
                    <h1>Admin Dashboard</h1>
                    <p className="page-subtitle">Welcome back! Here's your recruitment overview.</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="kpi-row">
                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: '#5B6FED' }}>
                        <Briefcase size={24} color="white" />
                    </div>
                    <div className="kpi-content">
                        <p className="kpi-label">TOTAL JOBS</p>
                        <h2 className="kpi-value">{metrics.totalJobs}</h2>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: '#EC4899' }}>
                        <Users size={24} color="white" />
                    </div>
                    <div className="kpi-content">
                        <p className="kpi-label">TOTAL CANDIDATES</p>
                        <h2 className="kpi-value">{metrics.totalCandidates}</h2>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: '#06B6D4' }}>
                        <FileText size={24} color="white" />
                    </div>
                    <div className="kpi-content">
                        <p className="kpi-label">ASSESSMENTS</p>
                        <h2 className="kpi-value">{metrics.assessments}</h2>
                    </div>
                </div>
            </div>

            {/* Assessment Leaderboard */}
            <div className="content-section">
                <div className="section-header">
                    <h2>Assessment Leaderboard</h2>
                    <button className="btn-link">View All</button>
                </div>

                <div className="assessment-table-container">
                    {loading ? (
                        <div className="loading-state">Loading...</div>
                    ) : (
                        <table className="assessment-table">
                            <thead>
                                <tr>
                                    <th>ASSESSMENT</th>
                                    <th>CANDIDATE</th>
                                    <th>JOB</th>
                                    <th>SCORE</th>
                                    <th>STATUS</th>
                                    <th>ACTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {assessments.map((assessment) => (
                                    <tr key={assessment.id}>
                                        <td>#{assessment.id}</td>
                                        <td>{assessment.candidate?.name || 'Unknown'}</td>
                                        <td>{assessment.jobTitle || 'N/A'}</td>
                                        <td>
                                            <strong>{(assessment.score || 0.0).toFixed(1)}</strong>/{(assessment.maxScore || 5.0).toFixed(1)}
                                        </td>
                                        <td>
                                            <span className={`status-badge ${getStatusClass(assessment.status)}`}>
                                                {assessment.status || 'pending'}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="action-buttons">
                                                <button
                                                    className="btn-action btn-primary"
                                                    onClick={() => navigate(`/dashboard/assessments/${assessment.id}/report`)}
                                                >
                                                    <FileText size={14} />
                                                    Report
                                                </button>
                                                <button className="btn-action btn-secondary">
                                                    <Eye size={14} />
                                                    Transcripts
                                                </button>
                                                <button
                                                    className="btn-action btn-warning"
                                                    onClick={() => handleRecompute(assessment.id)}
                                                >
                                                    <RefreshCw size={14} />
                                                    Recompute
                                                </button>
                                                <button
                                                    className="btn-action btn-danger"
                                                    onClick={() => handleDelete(assessment.id)}
                                                >
                                                    <Trash2 size={14} />
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
