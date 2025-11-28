# Walkthrough - Multilingual Gemini-Live Proctored Interview

## Overview
This system provides a complete interview platform with:
- **Candidate Interface**: Video recording, live transcription (simulated/ready for Gemini), and real-time proctoring alerts.
- **Backend**: FastAPI server handling sessions, media storage, and SQLite persistence.
- **Dashboard**: Reviewer interface to watch answers and check scores.

## Setup Instructions

### 1. Backend Setup
1. Navigate to `server/`:
   ```bash
   cd server
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python main.py
   ```
   Server will start at `http://localhost:8000`.

   **Docker Option**:
   ```bash
   docker build -t interview-server .
   docker run -p 8000:8000 -v $(pwd)/data:/app/data interview-server
   ```

### 2. Frontend Setup
1. Navigate to `client/`:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   Client will start at `http://localhost:5173`.

## Verification Steps

### 1. Candidate Flow
1. Open `http://localhost:5173`.
2. Click **Start Interview**.
3. Allow Camera/Microphone access.
4. Wait for the question to appear (Thinking time).
5. Recording starts automatically after 10s.
6. Speak into the microphone.
7. Click **Stop & Submit** or wait for timer.
8. Confirm "Next Question" or finish.

### 2. Proctoring Test
1. During the interview, cover your camera or turn off the lights.
2. Observe the "Low light" or "No face" alert in the side panel.
3. **Server Verification**: The server now also analyzes the frame sent with the event. Check `proctor_event` table or dashboard for "Server Verified" notes.

### 3. Media Cropping
1. After submitting an answer, check `server/data/media`.
2. You should see `cropped_...webm` files alongside the original recording (requires FFmpeg installed).

### 4. Dashboard
1. Go to `http://localhost:5173/dashboard`.
2. You should see the interview you just completed.
3. Click **View** to see the question and play back the recorded video.

## Key Features Implemented
- **Single Component UI**: `InterviewPage.jsx` handles the entire interview state machine.
- **Media Handling**: `interview.js` manages `MediaRecorder` and WebSocket streams.
- **Backend Persistence**: SQLite stores all metadata, questions, and paths to video files.
- **Proctoring**: 
    - Client-side: Brightness detection.
    - Server-side: OpenCV face detection and verification in `proctoring.py`.
- **Media Processing**: `media_processor.py` uses FFmpeg to crop videos to the face.

## Notes
- **Gemini Live**: The integration is mocked in `main.py` (`generate_question`) because valid API keys are required. To enable it, update the `TODO` section in `server/main.py` with the actual Vertex AI call using the keys from `.env`.
- **OpenCV**: Client-side structure is in place. To fully enable WASM OpenCV, add `<script src="opencv.js"></script>` to `index.html` and uncomment the logic in `interview.js`.
