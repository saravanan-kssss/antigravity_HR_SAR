import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AnimatedSidebar from './components/AnimatedSidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CandidatesPage from './pages/CandidatesPage';
import AssessmentsPage from './pages/AssessmentsPage';
import AssessmentReport from './pages/AssessmentReport';
import JobsPage from './pages/JobsPage';
import InterviewPage from './InterviewPage';
import OpenPositionsPage from './pages/OpenPositionsPage';
import ApplyJobPage from './pages/ApplyJobPage';
import MatchResultPage from './pages/MatchResultPage';
import AssessmentCompletePage from './pages/AssessmentCompletePage';
import './AppLayout.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
    return (
        <Router>
            <Routes>
                {/* Login Route */}
                <Route path="/login" element={<LoginPage />} />

                {/* Public candidate routes (no sidebar) */}
                <Route path="/" element={<OpenPositionsPage />} />
                <Route path="/jobs/:jobId/apply" element={<ApplyJobPage />} />
                <Route path="/applications/:applicationId/result" element={<MatchResultPage />} />
                <Route path="/interview" element={<InterviewPage />} />
                <Route path="/assessment-complete" element={<AssessmentCompletePage />} />

                {/* Protected Dashboard routes (with sidebar) */}
                <Route path="/dashboard" element={
                    <ProtectedRoute>
                        <div className="app-layout">
                            <AnimatedSidebar />
                            <main className="main-content">
                                <DashboardPage />
                            </main>
                        </div>
                    </ProtectedRoute>
                } />
                <Route path="/dashboard/jobs" element={
                    <ProtectedRoute>
                        <div className="app-layout">
                            <AnimatedSidebar />
                            <main className="main-content">
                                <JobsPage />
                            </main>
                        </div>
                    </ProtectedRoute>
                } />
                <Route path="/dashboard/candidates" element={
                    <ProtectedRoute>
                        <div className="app-layout">
                            <AnimatedSidebar />
                            <main className="main-content">
                                <CandidatesPage />
                            </main>
                        </div>
                    </ProtectedRoute>
                } />
                <Route path="/dashboard/assessments" element={
                    <ProtectedRoute>
                        <div className="app-layout">
                            <AnimatedSidebar />
                            <main className="main-content">
                                <AssessmentsPage />
                            </main>
                        </div>
                    </ProtectedRoute>
                } />
                <Route path="/dashboard/assessments/:id/report" element={
                    <ProtectedRoute>
                        <div className="app-layout">
                            <AnimatedSidebar />
                            <main className="main-content">
                                <AssessmentReport />
                            </main>
                        </div>
                    </ProtectedRoute>
                } />
            </Routes>
        </Router>
    );
}

export default App;
