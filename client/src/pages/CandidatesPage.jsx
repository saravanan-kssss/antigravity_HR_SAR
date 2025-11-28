import React, { useState, useEffect } from 'react';
import { Eye, Download, Trash2 } from 'lucide-react';
import './CandidatesPage.css';

const CandidatesPage = () => {
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCandidates();
    }, []);

    const fetchCandidates = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/candidates?page=1&limit=20');
            if (res.ok) {
                const data = await res.json();
                setCandidates(data.items || []);
            }
            setLoading(false);
        } catch (err) {
            console.error('Error fetching candidates:', err);
            setLoading(false);
        }
    };

    const getScoreBadgeClass = (score) => {
        if (score >= 8) return 'score-high';
        if (score >= 5) return 'score-mid';
        return 'score-low';
    };

    return (
        <div className="candidates-page">
            <div className="page-header">
                <h1>Candidates</h1>
            </div>

            {loading ? (
                <div className="loading-state">Loading candidates...</div>
            ) : (
                <div className="candidates-grid">
                    {candidates.map((candidate) => (
                        <div key={candidate.id} className="candidate-card">
                            <div className="candidate-header">
                                <div className="candidate-info">
                                    <div className="candidate-avatar">
                                        {candidate.name?.charAt(0).toUpperCase() || 'C'}
                                    </div>
                                    <div>
                                        <h3 className="candidate-name">{candidate.name || 'Unknown'}</h3>
                                        <p className="candidate-email">{candidate.email || 'N/A'}</p>
                                    </div>
                                </div>
                                <div className={`score-badge ${getScoreBadgeClass(candidate.overallScore || 0)}`}>
                                    {candidate.overallScore || 0}
                                </div>
                            </div>

                            <div className="candidate-details">
                                <div className="detail-row">
                                    <span className="detail-icon">📞</span>
                                    <span className="detail-text">{candidate.phone || '—'}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-icon">💼</span>
                                    <span className="detail-text">{candidate.appliedRole || '—'}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-icon">📅</span>
                                    <span className="detail-text">
                                        {candidate.createdAt ? new Date(candidate.createdAt).toLocaleDateString() : '—'}
                                    </span>
                                </div>
                            </div>

                            <div className="candidate-actions">
                                <button className="btn-card btn-view">
                                    <Eye size={16} />
                                    View
                                </button>
                                <button className="btn-card btn-download">
                                    <Download size={16} />
                                    Download
                                </button>
                                <button className="btn-card btn-delete">
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CandidatesPage;
