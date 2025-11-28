import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Eye, RefreshCw, Trash2 } from 'lucide-react';
import './AssessmentsPage.css';

const AssessmentsPage = () => {
    const navigate = useNavigate();
    const [assessments, setAssessments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const limit = 20;

    useEffect(() => {
        fetchAssessments();
    }, [page]);

    const fetchAssessments = async () => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/assessments?page=${page}&limit=${limit}`);
            if (res.ok) {
                const data = await res.json();
                setAssessments(data.items || []);
                setTotal(data.total || 0);
            }
        } catch (err) {
            console.error('Error fetching assessments:', err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusClass = (status) => {
        if (status === 'completed') return 'status-completed';
        if (status === 'in_progress') return 'status-in-progress';
        if (status === 'pending') return 'status-pending';
        return 'status-gray';
    };

    const getStatusBadgeClass = (status) => {
        if (status === 'completed') return 'badge-completed';
        if (status === 'in_progress') return 'badge-in-progress';
        if (status === 'pending') return 'badge-pending';
        return 'badge-gray';
    };

    const handleRecompute = async (id) => {
        if (!window.confirm('Recompute this assessment? This will re-evaluate all answers and regenerate feedback.')) return;
        
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/api/assessments/${id}/recompute`, { 
                method: 'POST' 
            });
            
            if (response.ok) {
                const data = await response.json();
                alert(`Assessment recomputed successfully!\nNew Score: ${data.overall_score_percent.toFixed(1)}%`);
                fetchAssessments(); // Refresh the list
            } else {
                alert('Failed to recompute assessment');
            }
        } catch (err) {
            console.error('Recompute error:', err);
            alert('Error recomputing assessment');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Delete this assessment? This will permanently remove all interview data, questions, answers, and transcripts.')) return;
        
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/api/assessments/${id}`, { 
                method: 'DELETE' 
            });
            
            if (response.ok) {
                alert('Assessment deleted successfully');
                fetchAssessments(); // Refresh the list
            } else {
                alert('Failed to delete assessment');
            }
        } catch (err) {
            console.error('Delete error:', err);
            alert('Error deleting assessment');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="assessments-page">
            <div className="page-header">
                <h1>Assessments</h1>
            </div>

            <div className="assessments-table-container">
                {loading ? (
                    <div className="loading-state">Loading assessments...</div>
                ) : assessments.length === 0 ? (
                    <div className="empty-state">No assessments found</div>
                ) : (
                    <table className="assessments-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>CANDIDATE</th>
                                <th>JOB</th>
                                <th>MATCH</th>
                                <th>SCORE</th>
                                <th>STATUS</th>
                                <th>CREATED</th>
                                <th>RECORDINGS</th>
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
                                        <span className="match-score">
                                            {assessment.matchScore ? `${assessment.matchScore.toFixed(1)}%` : 'N/A'}
                                        </span>
                                    </td>
                                    <td>
                                        <strong>{assessment.score?.toFixed(1) || '0.0'}</strong> / {assessment.maxScore?.toFixed(1) || '5.0'}
                                    </td>
                                    <td>
                                        <span className={`status-badge ${getStatusBadgeClass(assessment.status)}`}>
                                            {assessment.status || 'pending'}
                                        </span>
                                    </td>
                                    <td>{formatDate(assessment.createdAt)}</td>
                                    <td>
                                        <span className={assessment.hasRecordings ? 'has-recordings' : 'no-recordings'}>
                                            {assessment.hasRecordings ? 'Yes' : 'None'}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="action-buttons">
                                            <button
                                                className="btn-action btn-primary"
                                                onClick={() => navigate(`/dashboard/assessments/${assessment.id}/report`)}
                                                title="View Report"
                                            >
                                                <FileText size={14} />
                                                Report
                                            </button>
                                            <button 
                                                className="btn-action btn-secondary"
                                                title="View Transcripts"
                                            >
                                                <Eye size={14} />
                                                Transcripts
                                            </button>
                                            <button
                                                className="btn-action btn-warning"
                                                onClick={() => handleRecompute(assessment.id)}
                                                title="Recompute Score"
                                            >
                                                <RefreshCw size={14} />
                                                Recompute
                                            </button>
                                            <button
                                                className="btn-action btn-danger"
                                                onClick={() => handleDelete(assessment.id)}
                                                title="Delete Assessment"
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

            {/* Pagination */}
            {total > limit && (
                <div className="pagination">
                    <button
                        className="btn-page"
                        disabled={page === 1}
                        onClick={() => setPage(page - 1)}
                    >
                        Previous
                    </button>
                    <span className="page-info">
                        Page {page} of {Math.ceil(total / limit)}
                    </span>
                    <button
                        className="btn-page"
                        disabled={page >= Math.ceil(total / limit)}
                        onClick={() => setPage(page + 1)}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default AssessmentsPage;
