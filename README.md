# 🔍 TruthLayer — AI-Powered Fact-Checking Engine

> Upload any PDF. Our AI agent extracts every verifiable claim, cross-references it against **live web data**, and flags what's real, outdated, or simply false — in real time.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-truthlayer.vercel.app-6366f1?style=for-the-badge&logo=vercel)](https://truthlayer.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend%20API-Render-10b981?style=for-the-badge&logo=render)](https://truthlayer-api.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **PDF Upload** | Drag-and-drop or click-to-upload, supports PDFs up to 10 MB |
| 🤖 **Multi-LLM Claim Extraction** | Identifies 5–20 verifiable factual claims (stats, dates, financial/technical figures) |
| 🌐 **Live Web Verification** | Tavily Search API retrieves real-time evidence from authoritative sources (5 sources/claim) |
| ⚡ **Streaming Results** | Claims appear as they are verified via Server-Sent Events (SSE) — no waiting |
| 🏅 **Verdict System** | ✅ Verified · ⚠️ Inaccurate · ❌ False · ❓ Unverifiable |
| 📊 **Confidence Score** | Each verdict carries a 0–100% confidence percentage |
| 🔗 **Source Citations** | Every verdict links directly to the web sources used |
| 🔎 **Filter & Search** | Filter results by verdict type or search by keyword |
| 🔄 **LLM Failover** | Automatic fallback chain: Groq → Gemini → Ollama → Demo Mode |
| 🧪 **Demo Mode** | Test the UI with mock data when no API keys are configured |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (React 18 + Vite)                 │
│   PDF Upload → SSE Stream Reader → Live Claim Cards Display   │
└────────────────────────┬─────────────────────────────────────┘
                         │  POST /api/fact-check (multipart/form-data)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                        │
│                                                              │
│  ┌─────────────┐   ┌──────────────────┐   ┌──────────────┐  │
│  │ PDF Parser  │──▶│ Claim Extractor   │──▶│   Verifier   │  │
│  │ (PyMuPDF)   │   │ (AIClient)        │   │(Tavily+AI)   │  │
│  └─────────────┘   └──────────────────┘   └──────────────┘  │
│                              │                    │          │
│                 ┌────────────▼────────────────────▼──┐      │
│                 │         AIClient (Fallback Chain)    │      │
│                 │   Groq → Gemini → Ollama → Demo     │      │
│                 └────────────────────────────────────┘      │
│                                      SSE Stream ◀───────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Pipeline Steps

| Step | Agent | Action |
|------|-------|--------|
| 1 | `pdf_parser.py` | PyMuPDF extracts clean text from the uploaded PDF |
| 2 | `extractor.py` | AI identifies 5–20 verifiable claims (stats, dates, figures) |
| 3 | `verifier.py` | Tavily fetches live web evidence for each claim (advanced search) |
| 4 | `verifier.py` | AI reasons over the evidence and delivers a structured verdict |
| 5 | `main.py` | Results are streamed via SSE so users see verdicts as they arrive |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Vanilla CSS |
| **Backend** | Python 3.11, FastAPI, Uvicorn / Gunicorn |
| **PDF Processing** | PyMuPDF (`fitz`) |
| **AI — Primary** | Groq (Llama-3 / Mixtral, fastest) |
| **AI — Secondary** | Google Gemini 1.5 Flash (key rotation) |
| **AI — Tertiary** | Ollama Cloud API (open-source fallback) |
| **Web Search** | Tavily Search API (advanced, 5 results/claim) |
| **Streaming** | Server-Sent Events (SSE) |
| **Frontend Deploy** | Vercel |
| **Backend Deploy** | Render (Gunicorn + Uvicorn Worker) |

---

## 📁 Project Structure

```
truthlayer/
├── backend/
│   ├── main.py                  # FastAPI app + SSE streaming endpoint
│   ├── agents/
│   │   ├── extractor.py         # AI claim extraction agent
│   │   └── verifier.py          # Tavily + AI verification & adjudication agent
│   ├── utils/
│   │   ├── ai_client.py         # Unified AI client with Groq → Gemini → Ollama fallback
│   │   ├── gemini_client.py     # Gemini key-rotation client
│   │   ├── groq_client.py       # Groq API client
│   │   ├── ollama_client.py     # Ollama Cloud API client
│   │   └── pdf_parser.py        # PyMuPDF text extraction utility
│   ├── requirements.txt
│   ├── render.yaml              # Render deployment config
│   ├── .env.example             # Environment variable template
│   └── README.md                # Backend-specific documentation
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app with SSE state machine
│   │   ├── main.jsx             # React entry point
│   │   ├── index.css            # Global design system & animations
│   │   └── components/
│   │       ├── ClaimCard.jsx    # Individual claim result with verdict badge
│   │       ├── UploadZone.jsx   # Drag-and-drop PDF upload component
│   │       ├── ProgressBar.jsx  # Real-time progress indicator
│   │       └── ResultsPanel.jsx # Results panel with filters & summary stats
│   ├── index.html
│   ├── vite.config.js
│   ├── vercel.json              # Vercel deployment config (SPA routing fix)
│   ├── .env.example
│   └── README.md                # Frontend-specific documentation
├── render.yaml                  # Root-level render config reference
├── .gitignore
└── README.md
```

---

## 🚀 Local Development

### Prerequisites

- Python **3.11+**
- Node.js **18+**
- At least one of:
  - [Groq API Key](https://console.groq.com/) (free — fastest)
  - [Gemini API Key](https://aistudio.google.com/) (free tier)
  - [Ollama](https://ollama.com/) running locally
- [Tavily API Key](https://tavily.com/) — free tier (1,000 searches/month)

### 1. Clone the Repository

```bash
git clone https://github.com/abhishek-si-ngh/truthlayer.git
cd truthlayer
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
# Edit .env and add your API keys (see below)

# Start the API server
uvicorn main:app --reload --port 8000
```

#### `.env` Configuration

```env
# Add at least one AI provider key
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEYS=key1,key2          # Comma-separated for rotation
OLLAMA_API_KEY=your_ollama_key     # Optional — if using Ollama Cloud
OLLAMA_BASE_URL=http://localhost:11434  # Local Ollama endpoint

# Required for live web search
TAVILY_API_KEY=your_tavily_api_key_here

# Set to true to run UI with mock data (no API keys needed)
DEMO_MODE=false

# Comma-separated list of allowed frontend origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Create local environment file
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
# Open http://localhost:5173
```

---

## 🌐 Deployment

### Backend → Render

1. Connect your GitHub repo to [Render](https://render.com)
2. Create a new **Web Service** — Root Directory: `backend`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
5. Add **Environment Variables:**
   - `GROQ_API_KEY`
   - `GEMINI_API_KEYS` (comma-separated keys for rotation)
   - `TAVILY_API_KEY`
   - `ALLOWED_ORIGINS` → `https://your-frontend.vercel.app`
   - `DEMO_MODE` → `false`

> The root `render.yaml` file fully automates the above configuration.

### Frontend → Vercel

1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. **Root Directory:** `frontend`
3. **Framework Preset:** Vite
4. **Environment Variable:** `VITE_API_URL=https://truthlayer-api.onrender.com`
5. Click **Deploy**

---

## 🎯 Evaluation Notes — "Trap Document" Handling

This app is specifically designed to pass the **"Trap Document"** test:

| Scenario | How TruthLayer Handles It |
|----------|--------------------------|
| Outdated Statistics | Flagged as ⚠️ **Inaccurate** — correct current figure provided |
| Hallucinated Facts | Flagged as ❌ **False** — contradicting evidence cited |
| Correct Facts | Confirmed as ✅ **Verified** — source links included |
| No online footprint | Marked ❓ **Unverifiable** — with transparent reasoning |

---

## 🔑 API Keys — Where to Get Them

| Service | Free Tier | Link |
|---------|-----------|------|
| Groq | ✅ Yes (generous) | [console.groq.com](https://console.groq.com) |
| Google Gemini | ✅ Yes | [aistudio.google.com](https://aistudio.google.com) |
| Tavily | ✅ 1,000 searches/month | [tavily.com](https://tavily.com) |
| Ollama | ✅ Self-hosted | [ollama.com](https://ollama.com) |

---

## 📄 License

MIT License — Built as part of the **Cog Culture Management Trainee Assessment**.
