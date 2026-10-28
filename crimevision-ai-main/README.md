# 🔍 CrimeVision AI

**AI-Assisted Forensic Evidence Analysis System**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://crimevision-ai.streamlit.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Aditya2709--mishra%2Fcrimevision--ai-blue?logo=github)](https://github.com/Aditya2709-mishra/crimevision-ai)

> 🚀 **Live Demo on Streamlit Cloud:** [https://crimevision-ai.streamlit.app](https://crimevision-ai.streamlit.app)

CrimeVision AI is an academic project that demonstrates how artificial intelligence can assist in forensic evidence analysis. It allows investigators to upload images and audio files, analyze them using AI, and generate comprehensive reports.

> ⚠️ **Disclaimer**: This is an academic BTech project for demonstration purposes only. It is NOT intended for real forensic investigations. All AI-generated analysis uses cautious language and should never be treated as definitive evidence.

---

## ✨ Features

- **Case Management** — Create and manage forensic cases
- **Image Analysis** — AI-powered analysis of crime scene images (people, objects, weapons, scene description)
- **Audio Analysis** — Speech-to-text transcription and analysis of audio evidence
- **Timeline Generation** — Chronological timeline of events extracted from evidence
- **AI Case Summary** — Automated case summary generation
- **AI Chat** — Ask questions about the case evidence
- **PDF Reports** — Generate professional forensic analysis reports
- **Demo Mode** — Load fictional demo data for easy demonstration

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Python + FastAPI |
| Database | SQLite + SQLAlchemy |
| AI | Groq API (LLaMA Vision + Whisper) |
| PDF | ReportLab |

---

## 📁 Project Structure

```
crimevision-ai/
│
├── frontend/                   # React + Vite frontend
│   └── src/
│       ├── components/         # Reusable UI components
│       │   ├── Sidebar.jsx
│       │   ├── CreateCaseModal.jsx
│       │   ├── EvidenceUpload.jsx
│       │   ├── EvidenceCard.jsx
│       │   ├── AnalysisResults.jsx
│       │   ├── Timeline.jsx
│       │   ├── ChatBox.jsx
│       │   └── CaseSummary.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   └── CasePage.jsx
│       ├── services/
│       │   └── api.js
│       ├── App.jsx
│       └── main.jsx
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── database.py         # SQLite + SQLAlchemy setup
│   │   ├── models.py           # Database models
│   │   ├── routes/
│   │   │   ├── cases.py        # Case CRUD endpoints
│   │   │   ├── evidence.py     # Evidence upload & analysis
│   │   │   ├── chat.py         # AI chat endpoints
│   │   │   ├── report.py       # PDF report generation
│   │   │   ├── timeline.py     # Timeline generation
│   │   │   └── summary.py      # AI case summary
│   │   └── services/
│   │       └── groq_service.py # All Groq API interactions
│   │
│   ├── uploads/                # Uploaded evidence files
│   ├── reports/                # Generated PDF reports
│   ├── requirements.txt
│   └── .env                    # Groq API key (create from .env.example)
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Groq API Key** — Get one free at [console.groq.com](https://console.groq.com)

### 1. Clone / Navigate to the Project

```bash
cd crimevision-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_key_here

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be running at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be running at `http://localhost:5173`

### 4. Open the App

Go to [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📋 How to Use

1. **Create a Case** — Click "Create New Case" on the dashboard
2. **Upload Evidence** — Upload JPG/PNG images or MP3/WAV audio files
3. **Analyze Evidence** — Click "Analyze" on each evidence card
4. **View Findings** — See AI-generated analysis results
5. **Check Timeline** — View chronological events from evidence
6. **AI Summary** — Generate an overall case summary
7. **Chat with AI** — Ask questions about the case evidence
8. **Generate Report** — Download a PDF report of all findings

### Demo Mode

Click **"Load Demo Case"** on the dashboard to load fictional sample data for demonstration without needing to upload real files.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cases` | Create a new case |
| GET | `/api/cases` | List all cases |
| GET | `/api/cases/{id}` | Get case details |
| POST | `/api/cases/{id}/demo` | Load demo data |
| POST | `/api/cases/{id}/evidence` | Upload evidence |
| GET | `/api/cases/{id}/evidence` | List case evidence |
| POST | `/api/evidence/{id}/analyze` | Analyze evidence |
| POST | `/api/cases/{id}/chat` | Send chat message |
| GET | `/api/cases/{id}/chat` | Get chat history |
| GET | `/api/cases/{id}/timeline` | Get timeline |
| GET | `/api/cases/{id}/summary` | Get AI summary |
| GET | `/api/cases/{id}/report` | Download PDF report |

---

## 🤖 AI Models Used (via Groq)

| Task | Model |
|------|-------|
| Image Analysis | `llama-3.2-11b-vision-preview` |
| Audio Transcription | `whisper-large-v3-turbo` |
| Text Analysis & Chat | `llama-3.3-70b-versatile` |

---

## ⚠️ Limitations

- This is an **academic project** — not for real forensic use
- AI analysis may contain errors and should not be treated as factual
- All findings use cautious language ("appears to be", "possible", "uncertain")
- No authentication or user management is included
- The system does not identify individuals or make accusations
- Audio transcription accuracy depends on audio quality

---

## 👥 Team

*Add your team members here*

---

## 📄 License

This project is created for academic purposes as part of a BTech curriculum.
