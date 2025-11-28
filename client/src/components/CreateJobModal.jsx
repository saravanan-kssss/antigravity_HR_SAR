import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';
import './CreateJobModal.css';

const CreateJobModal = ({ mode, onClose, onJobCreated }) => {
    const [formData, setFormData] = useState({
        title: '',
        location: '',
        job_type: 'Full-Time',
        experience_required: '',
        description: '',
        vacancies: '1',
        skills: ''
    });
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [extracting, setExtracting] = useState(false);

    const handleFileChange = async (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            const allowedTypes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain',
                'text/markdown'
            ];
            
            if (!allowedTypes.includes(selectedFile.type)) {
                setError('Only PDF, DOC, DOCX, TXT, and MD files are accepted');
                return;
            }

            setFile(selectedFile);
            setFileName(selectedFile.name);
            setError('');

            // Auto-extract JD from file
            await extractJDFromFile(selectedFile);
        }
    };

    const extractJDFromFile = async (file) => {
        setExtracting(true);
        try {
            // Read file content
            const text = await file.text();
            
            // Simple extraction - in production, you'd use AI to parse this better
            // For now, we'll just use the text as description
            setFormData(prev => ({
                ...prev,
                description: text,
                // Try to extract title from first line
                title: text.split('\n')[0].replace(/^(job title:|title:)/i, '').trim().substring(0, 100) || 'Untitled Position'
            }));
        } catch (error) {
            console.error('Error extracting JD:', error);
            setError('Failed to extract job description from file');
        } finally {
            setExtracting(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.title || !formData.location || !formData.experience_required || !formData.description) {
            setError('Please fill all required fields');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: formData.title,
                    location: formData.location,
                    job_type: formData.job_type,
                    experience_required: formData.experience_required,
                    description: formData.description
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create job');
            }

            onJobCreated();
        } catch (error) {
            console.error('Error creating job:', error);
            setError('Failed to create job. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="create-job-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{mode === 'upload' ? 'Upload Job Description' : 'Create Job Manually'}</h2>
                    <button className="btn-close" onClick={onClose}>
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="job-form">
                    {mode === 'upload' && (
                        <div className="form-section">
                            <label>Upload JD File</label>
                            <div className="file-upload-area">
                                <input
                                    type="file"
                                    id="jd-upload"
                                    accept=".pdf,.doc,.docx,.txt,.md"
                                    onChange={handleFileChange}
                                    style={{ display: 'none' }}
                                />
                                <label htmlFor="jd-upload" className="file-upload-label">
                                    {fileName ? (
                                        <>
                                            <span className="file-name">{fileName}</span>
                                            {extracting && <span className="extracting">Extracting...</span>}
                                        </>
                                    ) : (
                                        <>
                                            <Upload size={32} />
                                            <span>Choose a file or drag & drop it here</span>
                                            <span className="file-hint">PDF, DOC, DOCX, TXT, MD</span>
                                        </>
                                    )}
                                </label>
                            </div>
                        </div>
                    )}

                    <div className="form-row">
                        <div className="form-group">
                            <label>Job Title *</label>
                            <input
                                type="text"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                placeholder="e.g., Machine Learning Engineer"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Location *</label>
                            <input
                                type="text"
                                value={formData.location}
                                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                placeholder="e.g., Chennai, India"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Job Type *</label>
                            <select
                                value={formData.job_type}
                                onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                            >
                                <option value="Full-Time">Full-Time</option>
                                <option value="Part-Time">Part-Time</option>
                                <option value="Contract">Contract</option>
                                <option value="Internship">Internship</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Experience Required *</label>
                            <input
                                type="text"
                                value={formData.experience_required}
                                onChange={(e) => setFormData({ ...formData, experience_required: e.target.value })}
                                placeholder="e.g., 2+ Years"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Job Description *</label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Enter the complete job description including responsibilities, requirements, and qualifications..."
                            rows={12}
                            required
                        />
                        <div className="char-count">{formData.description.length} characters</div>
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    <div className="modal-footer">
                        <button type="button" className="btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? 'Creating...' : 'Create Job'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateJobModal;
