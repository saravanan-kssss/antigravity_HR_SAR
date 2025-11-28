import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { InterviewManager } from './interview';
import LanguageSelection from './components/LanguageSelection';
import './interview.css';
import { AlertTriangle, Mic, Video, User, Mail, Eye, Users, Smartphone } from 'lucide-react';

const InterviewPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const applicationContext = location.state || {};
    
    const [stage, setStage] = useState(applicationContext.applicationId ? 'languageSelection' : 'details');
    const [candidateInfo, setCandidateInfo] = useState({ 
        name: applicationContext.candidateName || '', 
        email: applicationContext.candidateEmail || '' 
    });
    const [selectedLanguage, setSelectedLanguage] = useState('english');
    const [applicationId] = useState(applicationContext.applicationId || null);
    const [jobTitle] = useState(applicationContext.jobTitle || 'Telesales');
    const [interviewId, setInterviewId] = useState(null);
    const [status, setStatus] = useState('ready');
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [transcript, setTranscript] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [timeLeft, setTimeLeft] = useState(0);
    const [deviceStatus, setDeviceStatus] = useState({ video: false, audio: false });
    const [proctorStatus, setProctorStatus] = useState({
        faceDetected: true,
        eyeTracking: true,
        deviceCheck: true
    });
    const [totalQuestions, setTotalQuestions] = useState(5);
    const [isPlayingAudio, setIsPlayingAudio] = useState(false);

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const managerRef = useRef(null);
    const streamRef = useRef(null);
    const audioRef = useRef(null);

    const handleDetailsSubmit = (e) => {
        e.preventDefault();
        if (candidateInfo.name && candidateInfo.email) {
            setStage('languageSelection');
        }
    };

    const handleLanguageSelect = (language) => {
        console.log('🌍 Language selected:', language);
        setSelectedLanguage(language);
        console.log('✅ Language state updated to:', language);
        // Auto-proceed to device check after a short delay
        setTimeout(() => {
            console.log('⏭️ Proceeding to device check with language:', language);
            setStage('deviceCheck');
            initializeDevices();
        }, 500);
    };

    const initializeDevices = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: true
            });
            streamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }

            const videoTrack = stream.getVideoTracks()[0];
            const audioTrack = stream.getAudioTracks()[0];

            setDeviceStatus({
                video: videoTrack && videoTrack.enabled,
                audio: audioTrack && audioTrack.enabled
            });

        } catch (err) {
            console.error("Device access error:", err);
            alert("Please allow camera and microphone access.");
        }
    };

    // Auto-initialize language selection if coming from application
    useEffect(() => {
        if (applicationId && stage === 'languageSelection') {
            // Language selection is now required before device check
        }
    }, [applicationId]);

    const startInterviewSession = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/interviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    candidate_name: candidateInfo.name,
                    candidate_email: candidateInfo.email,
                    application_id: applicationId
                })
            });
            const data = await res.json();
            setInterviewId(data.interview_id);

            managerRef.current = new InterviewManager(
                data.interview_id,
                handleWebSocketMessage,
                handleProctorEvent
            );

            managerRef.current.stream = streamRef.current;
            managerRef.current.videoElement = videoRef.current;
            managerRef.current.canvasElement = canvasRef.current;

            managerRef.current.ws = new WebSocket(`ws://localhost:8000/ws/interview/${data.interview_id}`);
            managerRef.current.ws.onmessage = (event) => {
                const msgData = JSON.parse(event.data);
                handleWebSocketMessage(msgData);
            };

            managerRef.current.startProctoring();

            setStage('interview');

            // CRITICAL FIX: Re-attach video stream after React re-renders
            setTimeout(() => {
                if (videoRef.current && streamRef.current) {
                    console.log("Re-attaching video stream");
                    videoRef.current.srcObject = streamRef.current;
                    videoRef.current.play().catch(e => console.error("Video play error:", e));
                }
            }, 100);

            // Play greeting first
            await playGreeting(data.interview_id);

        } catch (err) {
            console.error("Failed to start interview:", err);
            alert("Failed to start interview: " + err.message);
        }
    };

    const playGreeting = async (id) => {
        try {
            console.log('🎤 Playing greeting...');
            const res = await fetch(`http://localhost:8000/api/interviews/${id}/greeting?language=${selectedLanguage}`);
            const data = await res.json();
            
            console.log("✅ Greeting received:", data.greeting);
            
            // Display greeting as current question
            setCurrentQuestion({
                text: data.greeting,
                seq: 0,
                isGreeting: true
            });
            
            setStatus('greeting');

            // Play greeting audio
            if (data.audio && audioRef.current) {
                try {
                    const audioBlob = base64ToBlob(data.audio, 'audio/mp3');
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioRef.current.src = audioUrl;
                    
                    setIsPlayingAudio(true);
                    
                    // Wait for audio to finish before starting questions
                    audioRef.current.onended = () => {
                        console.log("✅ Greeting audio finished");
                        setIsPlayingAudio(false);
                        // Start first question after greeting
                        setTimeout(() => {
                            getNextQuestion(id);
                        }, 1000);
                    };
                    
                    await audioRef.current.play();
                    console.log("✅ Greeting TTS playing");
                } catch (e) {
                    console.error("❌ Greeting TTS play error:", e);
                    setIsPlayingAudio(false);
                    // Fallback: start questions anyway
                    setTimeout(() => {
                        getNextQuestion(id);
                    }, 3000);
                }
            } else {
                console.log("⚠️ No greeting audio");
                // Fallback: start questions anyway
                setTimeout(() => {
                    getNextQuestion(id);
                }, 3000);
            }
        } catch (err) {
            console.error("Error playing greeting:", err);
            // Fallback: start questions anyway
            getNextQuestion(id);
        }
    };

    const getNextQuestion = async (id) => {
        try {
            console.log('🎯 Generating question with language:', selectedLanguage);
            const res = await fetch(`http://localhost:8000/api/interviews/${id}/questions/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count: 1, language: selectedLanguage, difficulty: 'Medium' })
            });
            const data = await res.json();
            console.log("✅ Question received:", data.question);
            console.log("📝 Question text:", data.question.text);
            setCurrentQuestion(data.question);
            setTotalQuestions(data.question.total_questions);

            setStatus('playing_question');
            setIsPlayingAudio(true);

            // Play audio if available
            if (data.question.audio && audioRef.current) {
                try {
                    console.log("✅ Audio data received");
                    const audioBlob = base64ToBlob(data.question.audio, 'audio/mp3');
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioRef.current.src = audioUrl;
                    
                    // Start thinking time AFTER audio finishes
                    audioRef.current.onended = () => {
                        console.log("✅ Question TTS finished, starting thinking time");
                        setIsPlayingAudio(false);
                        setStatus('thinking');
                        setTimeLeft(10);
                    };
                    
                    await audioRef.current.play();
                    console.log("✅ TTS playing");
                } catch (e) {
                    console.error("❌ TTS play error:", e);
                    setIsPlayingAudio(false);
                    // Fallback: start thinking time anyway
                    setStatus('thinking');
                    setTimeLeft(10);
                }
            } else {
                console.log("⚠️ No audio in response");
                setIsPlayingAudio(false);
                // Fallback: start thinking time anyway
                setStatus('thinking');
                setTimeLeft(10);
            }
        } catch (err) {
            console.error("Error getting question:", err);
            setIsPlayingAudio(false);
        }
    };

    const base64ToBlob = (base64, type) => {
        const binary = atob(base64);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            array[i] = binary.charCodeAt(i);
        }
        return new Blob([array], { type });
    };

    const handleWebSocketMessage = (msg) => {
        if (msg.type === 'transcript_update') {
            setTranscript(prev => {
                // If it's a final transcript, add it
                if (msg.is_final) {
                    return [...prev, { text: msg.text, isFinal: true }];
                } else {
                    // For interim results, replace the last interim or add new
                    const newTranscript = [...prev];
                    const lastIndex = newTranscript.length - 1;
                    
                    if (lastIndex >= 0 && !newTranscript[lastIndex].isFinal) {
                        newTranscript[lastIndex] = { text: msg.text, isFinal: false };
                    } else {
                        newTranscript.push({ text: msg.text, isFinal: false });
                    }
                    
                    return newTranscript;
                }
            });
        }
    };

    const handleProctorEvent = (event) => {
        setAlerts(prev => [...prev, { ...event, timestamp: new Date() }]);

        // Update proctoring status indicators dynamically
        if (event.type === 'low_light') {
            setProctorStatus(prev => ({ ...prev, deviceCheck: false }));
        } else if (event.type === 'frame_check') {
            // Periodic check - keep status
            setProctorStatus(prev => ({ ...prev, faceDetected: true }));
        }

        if (interviewId) {
            fetch(`http://localhost:8000/api/interviews/${interviewId}/proctor/event`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event_type: event.type,
                    confidence: event.confidence,
                    notes: event.notes,
                    frame_base64: event.frame_base64
                })
            });
        }
    };

    useEffect(() => {
        if (timeLeft > 0) {
            const timer = setInterval(() => setTimeLeft(t => t - 1), 1000);
            return () => clearInterval(timer);
        } else if (timeLeft === 0 && status === 'thinking') {
            startRecording();
        } else if (timeLeft === 0 && status === 'answering') {
            stopRecording();
        }
    }, [timeLeft, status]);

    const startRecording = () => {
        setStatus('answering');
        setTimeLeft(60);
        if (managerRef.current) {
            // Pass the selected interview language for STT
            managerRef.current.startRecording(selectedLanguage);
        }
    };

    const stopRecording = async () => {
        setStatus('processing');
        const blob = await managerRef.current.stopRecording();

        const formData = new FormData();
        formData.append('file', blob, 'answer.webm');
        formData.append('start_time', new Date().toISOString());
        formData.append('end_time', new Date().toISOString());

        const uploadRes = await fetch(`http://localhost:8000/api/interviews/${interviewId}/answers/${currentQuestion.id}/upload`, {
            method: 'POST',
            body: formData
        });

        const uploadData = await uploadRes.json();
        console.log('Answer uploaded:', uploadData);

        // Check if there are more questions
        const currentQuestionNum = currentQuestion.question_number || currentQuestion.seq;
        
        if (currentQuestionNum < totalQuestions) {
            // More questions remaining
            setTranscript([]);
            await getNextQuestion(interviewId);
        } else {
            // All questions answered - complete interview
            try {
                await fetch(`http://localhost:8000/api/interviews/${interviewId}/complete`, {
                    method: 'POST'
                });
                console.log('Interview marked as completed');
            } catch (err) {
                console.error('Error completing interview:', err);
            }
            
            // Stop camera/mic
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            
            // Navigate to completion page
            navigate('/assessment-complete', { 
                state: { interviewId } 
            });
        }
    };

    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            if (managerRef.current) {
                managerRef.current.cleanup();
            }
        };
    }, []);

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="logo">
                    <div className="logo-icon"></div>
                    matrimony.com
                </div>
                {candidateInfo.name && <div className="candidate-name">Candidate: {candidateInfo.name}</div>}
            </header>

            {/* Stage 1: Details Form */}
            {stage === 'details' && (
                <div className="stage-container">
                    <div className="details-form">
                        <h1>Welcome to the Interview</h1>
                        <p className="subtitle">Please enter your details to begin</p>

                        <form onSubmit={handleDetailsSubmit}>
                            <div className="form-group">
                                <label>
                                    <User size={18} />
                                    Full Name
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={candidateInfo.name}
                                    onChange={(e) => setCandidateInfo({ ...candidateInfo, name: e.target.value })}
                                    placeholder="Enter your full name"
                                    className="form-input"
                                />
                            </div>

                            <div className="form-group">
                                <label>
                                    <Mail size={18} />
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    required
                                    value={candidateInfo.email}
                                    onChange={(e) => setCandidateInfo({ ...candidateInfo, email: e.target.value })}
                                    placeholder="your.email@example.com"
                                    className="form-input"
                                />
                            </div>

                            <button type="submit" className="btn btn-primary btn-full">
                                Continue to Language Selection
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Stage 2: Language Selection */}
            {stage === 'languageSelection' && (
                <LanguageSelection
                    onLanguageSelect={handleLanguageSelect}
                    selectedLanguage={selectedLanguage}
                />
            )}

            {/* Stage 3: Device Check */}
            {stage === 'deviceCheck' && (
                <div className="stage-container">
                    <div className="device-check">
                        <h1>Camera & Microphone Check</h1>
                        <p className="subtitle">Please ensure your camera and microphone are working properly</p>

                        <div className="preview-box">
                            <video ref={videoRef} autoPlay muted playsInline className="preview-video" />
                            <canvas ref={canvasRef} style={{ display: 'none' }} width="300" height="150" />
                        </div>

                        <div className="device-status">
                            <div className={`status-item ${deviceStatus.video ? 'status-ok' : 'status-error'}`}>
                                <Video size={20} />
                                <span>Camera: {deviceStatus.video ? '✓ Working' : '✗ Not Detected'}</span>
                            </div>

                            <div className={`status-item ${deviceStatus.audio ? 'status-ok' : 'status-error'}`}>
                                <Mic size={20} />
                                <span>Microphone: {deviceStatus.audio ? '✓ Working' : '✗ Not Detected'}</span>
                            </div>
                        </div>

                        {deviceStatus.video && deviceStatus.audio ? (
                            <button className="btn btn-primary btn-large" onClick={startInterviewSession}>
                                Start Interview
                            </button>
                        ) : (
                            <div>
                                <p className="error-message">Please allow camera and microphone access</p>
                                <button className="btn btn-secondary" onClick={initializeDevices}>
                                    Retry Device Access
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Stage 4: Interview */}
            {stage === 'interview' && (
                <div className="interview-container">
                    <div className="interview-main">
                        <div className="question-area">
                            <div className="question-header">
                                {currentQuestion?.isGreeting ? (
                                    <span className="question-label">WELCOME</span>
                                ) : (
                                    <span className="question-label">
                                        QUESTION {currentQuestion?.question_number || currentQuestion?.seq || '-'} / {totalQuestions}
                                    </span>
                                )}
                                {status === 'greeting' && (
                                    <span className="status-badge greeting">🎤 Playing Greeting...</span>
                                )}
                                {status === 'playing_question' && (
                                    <span className="status-badge playing">🔊 Playing Question...</span>
                                )}
                                {status === 'thinking' && (
                                    <span className="status-badge thinking">⏱️ Thinking Time: {timeLeft}s</span>
                                )}
                                {status === 'answering' && (
                                    <span className="status-badge recording">🎙️ Recording: {timeLeft}s</span>
                                )}
                                {status === 'processing' && (
                                    <span className="status-badge processing">⚙️ Processing...</span>
                                )}
                            </div>
                            <div className="question-text">
                                {currentQuestion?.text || 'Loading...'}
                            </div>
                            {currentQuestion?.question_type && (
                                <div className="question-type-badge">
                                    {currentQuestion.question_type.toUpperCase()} QUESTION
                                </div>
                            )}
                        </div>

                        <div className="answer-area">
                            <div className="answer-header">YOUR ANSWER</div>
                            <div className="transcript-display">
                                {transcript.map((t, i) => (
                                    <span key={i} className={t.isFinal ? 'final' : 'partial'}>
                                        {t.text}{' '}
                                    </span>
                                ))}
                                {transcript.length === 0 && (
                                    <span className="placeholder">Your transcript will appear here...</span>
                                )}
                            </div>
                        </div>

                        <div className="interview-controls">
                            <button className="btn btn-outline">Exit</button>
                            {status === 'answering' && (
                                <button className="btn btn-primary" onClick={stopRecording}>
                                    Submit
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="interview-sidebar">
                        <div className="video-feed">
                            <video ref={videoRef} autoPlay muted playsInline className="interview-video" />
                            <div className="video-label">You</div>
                        </div>

                        <div className="proctoring-panel">
                            <h3>Proctoring Status</h3>
                            <div className="proctor-indicators">
                                <div className="proctor-item">
                                    <Eye size={16} />
                                    <span>Face Detection</span>
                                    <span className={`indicator-dot ${proctorStatus.faceDetected ? 'active' : ''}`}></span>
                                </div>
                                <div className="proctor-item">
                                    <Users size={16} />
                                    <span>Eye Tracking</span>
                                    <span className={`indicator-dot ${proctorStatus.eyeTracking ? 'active' : ''}`}></span>
                                </div>
                                <div className="proctor-item">
                                    <Smartphone size={16} />
                                    <span>Device Check</span>
                                    <span className={`indicator-dot ${proctorStatus.deviceCheck ? 'active' : ''}`}></span>
                                </div>
                            </div>

                            {alerts.length > 0 && (
                                <div className="recent-alerts">
                                    <h4>Recent Alerts</h4>
                                    {alerts.slice(-2).map((alert, i) => (
                                        <div key={i} className="alert-item">
                                            <AlertTriangle size={14} />
                                            <span>{alert.notes}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Hidden audio player for TTS */}
            <audio ref={audioRef} style={{ display: 'none' }} />
        </div>
    );
};

export default InterviewPage;
