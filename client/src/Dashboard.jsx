import React, { useState, useEffect } from 'react';
import {
    Users, TrendingUp, Clock, CheckCircle, Search, Filter,
    Download, Play, Eye, FileText, BarChart3, Calendar,
    ChevronRight, Star, AlertCircle, Video
} from 'lucide-react';
import './dashboard.css';

const Dashboard = () => {
    const [interviews, setInterviews] = useState([]);
    const [selectedInterview, setSelectedInterview] = useState(null);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchInterviews();
    }, []);

    const fetchInterviews = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/interviews/recent');
            const data = await res.json();
            setInterviews(data.interviews || []);
            setLoading(false);
        } catch (err) {
            console.error('Error fetching interviews:', err);
            setLoading(false);
        }
    };

    const fetchInterviewDetails = async (id) => {
        try {
            const res = await fetch(`http://localhost:8000/api/interviews/${id}`);
            const data = await res.json();
            setSelectedInterview(data);
        } catch (err) {
            console.error('Error fetching interview details:', err);
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            'completed': 'status-completed',
            'in_progress': 'status-progress',
            'pending': 'status-pending'
        };
        return colors[status] || 'status-pending';
    };

    const filteredInterviews = interviews.filter(interview => {
        const matchesSearch = interview.candidate_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            interview.candidate_email?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesFilter = filterStatus === 'all' || interview.status === filterStatus;
        return matchesSearch && matchesFilter;
    });

    // Mock KPI data
    const kpiData = {
        totalCandidates: interviews.length,
        avgScore: 78,
        interviewsToday: interviews.filter(i => {
            const today = new Date().toDateString();
            return new Date(i.created_at).toDateString() === today;
        }).length,
        completed: interviews.filter(i => i.status === 'completed').length
    };

    return (
        <div className="dashboard-container">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left">
                    <div className="logo-section">
                        <div className="logo-icon"></div>
                        <h1>matrimony.com</h1>
                    </div>
                    <span className="header-subtitle">Interview Dashboard</span>
                </div>

                <div className="header-center">
                    <div className="search-bar">
                        <Search size={18} />
                        <input
                            type="text"
                            placeholder="Search candidates..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </div>

                <div className="header-right">
                    <button className="icon-btn">
                        <Calendar size={20} />
                    </button>
                    <button className="icon-btn">
                        <Download size={20} />
                    </button>
                    <div className="user-avatar">
                        <span>HR</span>
                    </div>
                </div>
            </header>

            <div className="dashboard-layout">
                {/* Sidebar */}
                <aside className="dashboard-sidebar">
                    <nav className="sidebar-nav">
                        <a href="#" className="nav-item active">
                            <BarChart3 size={20} />
                            <span>Dashboard</span>
                        </a>
                        <a href="#" className="nav-item">
                            <Users size={20} />
                            <span>Candidates</span>
                        </a>
                        <a href="#" className="nav-item">
                            <FileText size={20} />
                            <span>Reports</span>
                        </a>
                        <a href="#" className="nav-item">
                            <Star size={20} />
                            <span>Analytics</span>
                        </a>
                    </nav>

                    <div className="sidebar-filters">
                        <h3>Filters</h3>
                        <div className="filter-group">
                            <label>Status</label>
                            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                                <option value="all">All</option>
                                <option value="completed">Completed</option>
                                <option value="in_progress">In Progress</option>
                                <option value="pending">Pending</option>
                            </select>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="dashboard-main">
                    {!selectedInterview ? (
                        <>
                            {/* KPI Cards */}
                            <div className="kpi-grid">
                                <div className="kpi-card">
                                    <div className="kpi-icon" style={{ background: '#EBF5FF' }}>
                                        <Users size={24} color="#2B6CB0" />
                                    </div>
                                    <div className="kpi-content">
                                        <p className="kpi-label">Total Candidates</p>
                                        <h2 className="kpi-value">{kpiData.totalCandidates}</h2>
                                        <span className="kpi-trend positive">+12% this week</span>
                                    </div>
                                </div>

                                <div className="kpi-card">
                                    <div className="kpi-icon" style={{ background: '#F0FDF4' }}>
                                        <TrendingUp size={24} color="#16A34A" />
                                    </div>
                                    <div className="kpi-content">
                                        <p className="kpi-label">Avg Score</p>
                                        <h2 className="kpi-value">{kpiData.avgScore}%</h2>
                                        <span className="kpi-trend positive">+5% vs last month</span>
                                    </div>
                                </div>

                                <div className="kpi-card">
                                    <div className="kpi-icon" style={{ background: '#FEF3C7' }}>
                                        <Clock size={24} color="#D97706" />
                                    </div>
                                    <div className="kpi-content">
                                        <p className="kpi-label">Today's Interviews</p>
                                        <h2 className="kpi-value">{kpiData.interviewsToday}</h2>
                                        <span className="kpi-trend neutral">Active now</span>
                                    </div>
                                </div>

                                <div className="kpi-card">
                                    <div className="kpi-icon" style={{ background: '#F3E8FF' }}>
                                        <CheckCircle size={24} color="#9333EA" />
                                    </div>
                                    <div className="kpi-content">
                                        <p className="kpi-label">Completed</p>
                                        <h2 className="kpi-value">{kpiData.completed}</h2>
                                        <span className="kpi-trend positive">{Math.round((kpiData.completed / kpiData.totalCandidates) * 100)}% completion</span>
                                    </div>
                                </div>
                            </div>

                            {/* Interviews Table */}
                            <div className="content-card">
                                <div className="card-header">
                                    <h2>Recent Interviews</h2>
                                    <div className="card-actions">
                                        <button className="btn-secondary">
                                            <Filter size={16} />
                                            Filter
                                        </button>
                                        <button className="btn-secondary">
                                            <Download size={16} />
                                            Export
                                        </button>
                                    </div>
                                </div>

                                <div className="table-container">
                                    {loading ? (
                                        <div className="loading-state">
                                            <div className="spinner"></div>
                                            <p>Loading interviews...</p>
                                        </div>
                                    ) : filteredInterviews.length === 0 ? (
                                        <div className="empty-state">
                                            <Users size={48} color="#CBD5E1" />
                                            <p>No interviews found</p>
                                        </div>
                                    ) : (
                                        <table className="data-table">
                                            <thead>
                                                <tr>
                                                    <th>Candidate</th>
                                                    <th>Email</th>
                                                    <th>Status</th>
                                                    <th>Created</th>
                                                    <th>Questions</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {filteredInterviews.map((interview) => (
                                                    <tr key={interview.id}>
                                                        <td>
                                                            <div className="candidate-cell">
                                                                <div className="candidate-avatar">
                                                                    {interview.candidate_name?.charAt(0).toUpperCase() || 'C'}
                                                                </div>
                                                                <span className="candidate-name">{interview.candidate_name || 'Unknown'}</span>
                                                            </div>
                                                        </td>
                                                        <td className="text-secondary">{interview.candidate_email || 'N/A'}</td>
                                                        <td>
                                                            <span className={`status-badge ${getStatusColor(interview.status)}`}>
                                                                {interview.status || 'pending'}
                                                            </span>
                                                        </td>
                                                        <td className="text-secondary">
                                                            {new Date(interview.created_at).toLocaleDateString()}
                                                        </td>
                                                        <td className="text-secondary">{interview.question_count || 0}</td>
                                                        <td>
                                                            <button
                                                                className="btn-action"
                                                                onClick={() => fetchInterviewDetails(interview.id)}
                                                            >
                                                                <Eye size={16} />
                                                                View Details
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    )}
                                </div>
                            </div>
                        </>
                    ) : (
                        /* Interview Details View */
                        <div className="interview-details">
                            <div className="details-header">
                                <button className="btn-back" onClick={() => setSelectedInterview(null)}>
                                    ← Back to List
                                </button>
                                <h2>Interview Details: {selectedInterview.candidate_name}</h2>
                                <div className="details-actions">
                                    <button className="btn-secondary">
                                        <Download size={16} />
                                        Export PDF
                                    </button>
                                </div>
                            </div>

                            <div className="details-grid">
                                {/* Candidate Info Card */}
                                <div className="content-card">
                                    <h3>Candidate Information</h3>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="info-label">Name</span>
                                            <span className="info-value">{selectedInterview.candidate_name}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Email</span>
                                            <span className="info-value">{selectedInterview.candidate_email}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Status</span>
                                            <span className={`status-badge ${getStatusColor(selectedInterview.status)}`}>
                                                {selectedInterview.status}
                                            </span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Created</span>
                                            <span className="info-value">
                                                {new Date(selectedInterview.created_at).toLocaleString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Questions & Answers */}
                                <div className="content-card full-width">
                                    <h3>Questions & Answers</h3>
                                    {selectedInterview.questions && selectedInterview.questions.length > 0 ? (
                                        <div className="questions-list">
                                            {selectedInterview.questions.map((question, idx) => (
                                                <div key={question.id} className="question-item">
                                                    <div className="question-header">
                                                        <span className="question-number">Q{idx + 1}</span>
                                                        <p className="question-text">{question.text}</p>
                                                    </div>

                                                    {question.answer && (
                                                        <div className="answer-section">
                                                            {question.answer.video_path ? (
                                                                <div className="video-player">
                                                                    <video
                                                                        controls
                                                                        src={`http://localhost:8000${question.answer.video_path}`}
                                                                        className="answer-video"
                                                                    >
                                                                        Your browser does not support video playback.
                                                                    </video>
                                                                    <div className="video-meta">
                                                                        <Video size={14} />
                                                                        <span>Duration: {question.answer.duration || '0s'}</span>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <div className="no-video">
                                                                    <AlertCircle size={20} />
                                                                    <span>No video recorded</span>
                                                                </div>
                                                            )}

                                                            {question.answer.transcript && (
                                                                <div className="transcript-box">
                                                                    <h4>Transcript</h4>
                                                                    <p>{question.answer.transcript}</p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="empty-state">
                                            <FileText size={32} color="#CBD5E1" />
                                            <p>No questions answered yet</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default Dashboard;
