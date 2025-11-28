# Interview Platform Dashboard

Modern recruitment dashboard with AI-powered interview assessment system.

## Features

- **Gradient Blue Sidebar Navigation** - Clean, modern navigation matching matrimony.com branding
- **KPI Dashboard** - Total Jobs, Candidates, and Assessments at a glance
- **Assessment Leaderboard** - View, manage, and recompute candidate assessments
- **Candidate Management** - Grid view with scores, contact info, and actions
- **Video Interview System** - Record and review candidate responses
- **AI-Powered TTS** - Questions spoken in multiple languages using Google Cloud TTS
- **Proctoring System** - Real-time monitoring with OpenCV face detection

## Tech Stack

### Frontend
- React 18
- React Router v6
- Lucide React Icons
- CSS Modules

### Backend
- FastAPI
- SQLite Database
- Google Gemini AI (Question Generation)
- Google Cloud Text-to-Speech
- WebSockets (Real-time communication)
- OpenCV (Proctoring)

## Running Locally

### Prerequisites
- Node.js 16+ and npm
- Python 3.9+
- Google Cloud credentials (for TTS)

### Backend Setup

1. Navigate to server directory:
```bash
cd server
```

2. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `server/.env`:
```env
GEMINI_LIVE_MODEL=gemini-1.5-flash
GEMINI_LIVE_VOICE=Puck
GEMINI_LIVE_LANGUAGE=tamil
GCP_PROJECT_ID=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_APPLICATION_CREDENTIALS=./voicebot-my-project-75138-004a5ee87934.json
```

5. Start the backend server:
```bash
python main.py
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Dashboard Routes

- `/dashboard` - Main dashboard with KPIs and assessment leaderboard
- `/candidates` - Candidate grid view
- `/jobs` - Job listings (coming soon)
- `/assessments` - Full assessment management (coming soon)
- `/interview` - Live interview interface (no sidebar)

## API Endpoints

### Dashboard & Metrics
- `GET /api/metrics/overview?range=30d` - KPI metrics
- `GET /api/candidates?page=1&limit=20&search=` - Paginated candidates
- `GET /api/assessments?page=1&limit=20` - Paginated assessments

### Interview Management
- `POST /api/interviews` - Create new interview
- `GET /api/interviews/{id}` - Get interview details
- `GET /api/interviews/recent` - Recent interviews list

### Questions & Answers
- `POST /api/interviews/{id}/questions/generate` - Generate AI question with TTS
- `POST /api/interviews/{id}/answers/{question_id}/upload` - Upload video answer

### Assessment Actions
- `POST /api/assessments/{id}/recompute` - Recompute assessment scores
- `DELETE /api/assessments/{id}` - Delete assessment

### Proctoring
- `POST /api/interviews/{id}/proctor/event` - Log proctoring event

### Media
- `GET /data/media/{filename}` - Serve recorded videos

## Database Schema

SQLite database with tables:
- `interview` - Interview sessions
- `question` - Generated questions
- `answer` - Candidate responses with video paths
- `proctor_event` - Proctoring alerts and snapshots

## Environment Variables

### Required
- `GOOGLE_API_KEY` - Gemini AI API key
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account JSON
- `GCP_PROJECT_ID` - Google Cloud project ID

### Optional
- `GEMINI_LIVE_LANGUAGE` - TTS language (default: tamil)
- `GEMINI_LIVE_VOICE` - TTS voice name (default: Puck)

## Troubleshooting

### TTS Not Working
1. Ensure Cloud Text-to-Speech API is enabled in Google Cloud Console
2. Wait 2-3 minutes after enabling for propagation
3. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
4. Verify service account has TTS permissions

### Videos Not Showing
1. Check backend is serving static files: `http://localhost:8000/data/media/`
2. Verify video files exist in `server/data/media/`
3. Check browser console for CORS errors

### Frontend Not Connecting
1. Ensure backend is running on port 8000
2. Check CORS is enabled in `main.py`
3. Verify no firewall blocking localhost connections

## Development Notes

- Videos are stored in `server/data/media/`
- Proctoring frames in `server/data/frames/`
- Database file: `server/interview_platform.db`
- Frontend uses React Router for navigation
- Sidebar is fixed, main content scrolls

## Next Steps

1. Add Jobs table and CRUD operations
2. Implement full assessment detail page with:
   - Doughnut chart for overall score
   - Topic-wise horizontal bars
   - Transcript with video player sync
   - Proctoring event timeline
3. Add export to PDF functionality
4. Implement real-time WebSocket updates
5. Add user authentication
6. Deploy to production

## License

Proprietary - matrimony.com
