// interview.js

export class InterviewManager {
    constructor(interviewId, onMessage, onProctorEvent) {
        this.interviewId = interviewId;
        this.onMessage = onMessage;
        this.onProctorEvent = onProctorEvent;
        this.ws = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.stream = null;
        this.videoElement = null;
        this.canvasElement = null;
        this.proctorInterval = null;
    }

    async init(videoElement, canvasElement) {
        this.videoElement = videoElement;
        this.canvasElement = canvasElement;

        try {
            // Get media stream
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });

            // Set video source
            if (videoElement) {
                videoElement.srcObject = this.stream;
                // Ensure video plays
                videoElement.onloadedmetadata = () => {
                    videoElement.play().catch(err => {
                        console.error("Video play error:", err);
                    });
                };
            }

            // Connect WS
            this.ws = new WebSocket(`ws://localhost:8000/ws/interview/${this.interviewId}`);
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.onMessage(data);
            };

            this.ws.onerror = (error) => {
                console.error("WebSocket error:", error);
            };

            // Start Proctoring Loop
            this.startProctoring();

        } catch (err) {
            console.error("Error initializing media:", err);
            throw err;
        }
    }

    startRecording(language = 'en-US') {
        if (!this.stream) {
            console.error("No stream available for recording");
            return;
        }

        this.recordedChunks = [];

        // Check for supported mime types
        let mimeType = 'video/webm;codecs=vp9';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'video/webm;codecs=vp8';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'video/webm';
            }
        }

        this.mediaRecorder = new MediaRecorder(this.stream, {
            mimeType: mimeType,
            videoBitsPerSecond: 2500000
        });

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                this.recordedChunks.push(event.data);
            }
        };

        this.mediaRecorder.onerror = (event) => {
            console.error("MediaRecorder error:", event);
        };

        this.mediaRecorder.start(100); // Collect data every 100ms
        console.log("Recording started");

        // Start Speech-to-Text with specified language
        this.startSpeechRecognition(language);
    }

    startSpeechRecognition(language = 'en-US') {
        // Check if browser supports Web Speech API
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn("Speech Recognition not supported in this browser");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;
        
        // Map language codes for speech recognition
        const langMap = {
            'tamil': 'ta-IN',
            'hindi': 'hi-IN',
            'english': 'en-US',
            'telugu': 'te-IN',
            'kannada': 'kn-IN'
        };
        
        this.recognition.lang = langMap[language.toLowerCase()] || language || 'en-US';
        console.log(`Speech recognition language set to: ${this.recognition.lang}`);

        this.recognition.onresult = (event) => {
            try {
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    
                    if (event.results[i].isFinal) {
                        console.log(`Final transcript: ${transcript}`);
                        
                        // Send final transcript to callback
                        this.onMessage({
                            type: 'transcript_update',
                            text: transcript,
                            is_final: true,
                            timestamp: new Date().toISOString()
                        });

                        // Send to server via WebSocket
                        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                            this.ws.send(JSON.stringify({
                                type: 'transcript_chunk',
                                interview_id: this.interviewId,
                                text: transcript,
                                is_final: true,
                                timestamp: new Date().toISOString()
                            }));
                        }
                    } else {
                        // Send interim transcript to callback
                        this.onMessage({
                            type: 'transcript_update',
                            text: transcript,
                            is_final: false,
                            timestamp: new Date().toISOString()
                        });
                    }
                }
            } catch (err) {
                console.error("Error processing speech result:", err);
            }
        };

        this.recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            
            // Auto-restart on certain errors
            if (event.error === 'no-speech' || event.error === 'audio-capture') {
                console.log("Attempting to restart speech recognition...");
                setTimeout(() => {
                    if (this.recognition && this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                        try {
                            this.recognition.start();
                            console.log("Speech recognition restarted");
                        } catch (err) {
                            console.error("Failed to restart recognition:", err);
                        }
                    }
                }, 1000);
            }
        };

        this.recognition.onend = () => {
            console.log("Speech recognition ended");
            
            // Auto-restart if still recording
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                console.log("Auto-restarting speech recognition...");
                try {
                    this.recognition.start();
                    console.log("Speech recognition restarted automatically");
                } catch (err) {
                    console.error("Failed to auto-restart recognition:", err);
                }
            }
        };

        try {
            this.recognition.start();
            console.log("Speech recognition started successfully");
        } catch (err) {
            console.error("Error starting speech recognition:", err);
            // Retry once after a short delay
            setTimeout(() => {
                try {
                    this.recognition.start();
                    console.log("Speech recognition started on retry");
                } catch (retryErr) {
                    console.error("Failed to start recognition on retry:", retryErr);
                }
            }, 500);
        }
    }

    stopSpeechRecognition() {
        if (this.recognition) {
            try {
                this.recognition.stop();
                console.log("Speech recognition stopped");
            } catch (err) {
                console.error("Error stopping speech recognition:", err);
            }
        }
    }

    async stopRecording() {
        // Stop speech recognition
        this.stopSpeechRecognition();

        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder) {
                reject(new Error("No media recorder available"));
                return;
            }

            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
                console.log("Recording stopped, blob size:", blob.size);
                resolve(blob);
            };

            this.mediaRecorder.stop();
        });
    }

    startProctoring() {
        // Simple client-side proctoring simulation using Canvas

        this.proctorInterval = setInterval(() => {
            if (!this.videoElement || !this.canvasElement) return;

            const ctx = this.canvasElement.getContext('2d');

            try {
                ctx.drawImage(this.videoElement, 0, 0, 300, 150);

                // Get image data to check brightness (Low light detection)
                const frame = ctx.getImageData(0, 0, 300, 150);
                const data = frame.data;
                let colorSum = 0;

                for (let x = 0, len = data.length; x < len; x += 4) {
                    const r = data[x];
                    const g = data[x + 1];
                    const b = data[x + 2];
                    const avg = Math.floor((r + g + b) / 3);
                    colorSum += avg;
                }

                const brightness = Math.floor(colorSum / (300 * 150));

                if (brightness < 30) {
                    this.onProctorEvent({
                        type: 'low_light',
                        confidence: 0.8,
                        notes: 'Environment too dark (brightness: ' + brightness + ')'
                    });
                }

                // Get frame as base64 for server-side analysis (every 5 seconds)
                if (Math.random() < 0.2) { // 20% chance = ~every 5 intervals
                    const frameDataUrl = this.canvasElement.toDataURL('image/jpeg', 0.8);
                    this.onProctorEvent({
                        type: 'frame_check',
                        confidence: 1.0,
                        notes: 'Periodic frame check',
                        frame_base64: frameDataUrl
                    });
                }

            } catch (err) {
                console.error("Proctoring error:", err);
            }

        }, 2000); // Check every 2 seconds
    }

    cleanup() {
        this.stopSpeechRecognition();
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        if (this.ws) {
            this.ws.close();
        }
        if (this.proctorInterval) {
            clearInterval(this.proctorInterval);
        }
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
    }
}
