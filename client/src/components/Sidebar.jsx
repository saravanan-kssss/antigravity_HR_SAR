import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Users, FileText, LogOut } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('rememberMe');
        navigate('/login');
    };

    const navItems = [
        { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/dashboard/jobs', icon: Briefcase, label: 'Jobs' },
        { path: '/dashboard/candidates', icon: Users, label: 'Candidates' },
        { path: '/dashboard/assessments', icon: FileText, label: 'Assessments' },
    ];

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h1 className="sidebar-logo">matrimony.com</h1>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    <p className="nav-label">NAVIGATION</p>
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-link ${isActive ? 'active' : ''}`}
                            >
                                <Icon size={20} />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </div>

                <div className="nav-section nav-bottom">
                    <button className="nav-link logout-btn" onClick={handleLogout}>
                        <LogOut size={20} />
                        <span>Logout</span>
                    </button>
                </div>
            </nav>
        </div>
    );
};

export default Sidebar;
