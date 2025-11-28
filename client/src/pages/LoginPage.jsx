import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Orb from '../components/Orb';
import { User, Lock, ArrowRight } from 'lucide-react';
import './LoginPage.css';

const LoginPage = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        await new Promise(resolve => setTimeout(resolve, 600));

        if (username === 'admin' && password === 'hr2025') {
            localStorage.setItem('isAuthenticated', 'true');
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
            }
            navigate('/dashboard');
        } else {
            setError('Invalid username or password');
            setIsLoading(false);
        }
    };

    return (
        <div className="login-page">
            {/* Centered Orb Background */}
            <div className="login-orb-container">
                <Orb
                    hoverIntensity={0.8}
                    rotateOnHover={true}
                    hue={280}
                    forceHoverState={false}
                />
            </div>

            {/* Centered Login Content */}
            <div className="login-content">
                {/* Brand Logo - Red matrimony.com */}
                <h1 className="brand-logo">matrimony.com</h1>
                <p className="brand-subtitle">AI-Powered Recruitment Platform</p>

                {/* Login Form */}
                <div className="login-form-container">
                    <h2 className="form-title">Welcome Back</h2>
                    <p className="form-subtitle">Sign in to access your HR dashboard</p>

                    {error && (
                        <div className="error-alert">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="login-form">
                        <div className="form-group">
                            <label className="form-label">Username</label>
                            <div className="input-wrapper">
                                <User size={0} className="input-icon" />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="admin"
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <div className="input-wrapper">
                                <Lock size={0} className="input-icon" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••"
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-options">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={rememberMe}
                                    onChange={(e) => setRememberMe(e.target.checked)}
                                    className="checkbox-input"
                                />
                                <span>Remember me</span>
                            </label>
                            <a href="#" className="forgot-link">Forgot password?</a>
                        </div>

                        <button
                            type="submit"
                            className="submit-btn"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <span className="spinner"></span>
                            ) : (
                                <>
                                    Sign In
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </form>

                    
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
