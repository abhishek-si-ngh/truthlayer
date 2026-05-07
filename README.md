# 🔍 TruthLayer — AI-Powered Fact-Checking Engine

> Upload any PDF. Our AI agent extracts every verifiable claim, cross-references it against **live web data**, and flags what's real, outdated, or simply false.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-6366f1?style=for-the-badge)](https://truthlayer.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend%20API-Render-10b981?style=for-the-badge)](https://truthlayer-api.onrender.com)

---

## ✨ Features

- **PDF Upload** — Drag-and-drop or click-to-upload, up to 10MB
- **AI Claim Extraction** — Gemini 1.5 Flash identifies all verifiable factual claims (stats, dates, financial figures, technical metrics)
- **Live Web Verification** — Tavily Search API retrieves real-time evidence from authoritative sources
- **Streaming Results** — Claims are displayed as they're verified (Server-Sent Events), no waiting for all results
- **Verdict System** — Each claim gets a clear verdict:
  - ✅ **Verified** — Supported by live evidence
  - ⚠️ **Inaccurate** — Contains outdated or wrong data (with correction provided)
  - ❌ **False** — Directly contradicts credible sources
  - ❓ **Unverifiable** — Insufficient evidence found
- **Confidence Score** — Each verdict includes a confidence percentage
- **Source Citations** — Every verdict links to the sources used
- **Filter & Search** — Filter results by verdict type

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React/Vite)                 │
│  PDF Upload → SSE Stream Reader → Live Claim Cards Display   │
└─────────────────────────┬───────────────────────────────────┘
                          │ POST /api/fact-check (multipart)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│                                                             │
│  ┌─────────────┐   ┌──────────────────┐   ┌─────────────┐  │
│  │ PDF Parser  │──▶│ Claim Extractor   │──▶│  Verifier   │  │
│  │ (PyMuPDF)   │   │ (Gemini 1.5 Flash)│   │(Gemini+Tavily)│ │
│  └─────────────┘   └──────────────────┘   └─────────────┘  │
│                                                  │          │
│                          SSE Stream ◀────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Steps
1. **Parse** — PyMuPDF extracts clean text from the uploaded PDF
2. **Extract** — Gemini identifies 5–20 verifiable claims (stats, dates, figures)
3. **Search** — Tavily fetches live web evidence for each claim (advanced search, 5 sources/claim)
4. **Adjudicate** — Gemini reasons over the evidence and delivers a structured verdict
5. **Stream** — Results are streamed via SSE so users see verdicts as they arrive

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite, Vanilla CSS |
| Backend | Python 3.11, FastAPI |
| PDF Processing | PyMuPDF (fitz) |
| AI Reasoning | Google Gemini 1.5 Flash |
| Web Search | Tavily Search API |
| Streaming | Server-Sent Events (SSE) |
| Frontend Deploy | Vercel |
| Backend Deploy | Render |

---

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Gemini API Key](https://aistudio.google.com/) (free)
- [Tavily API Key](https://tavily.com/) (free tier — 1000 searches/month)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys

uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
# Open http://localhost:3000
```

---

## 🌐 Deployment

### Backend (Render)
1. Connect your GitHub repo to [Render](https://render.com)
2. Create a new **Web Service** pointing to the `/backend` directory
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables: `GEMINI_API_KEY`, `TAVILY_API_KEY`

### Frontend (Vercel)
1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. Set **Root Directory**: `frontend`
3. Add Environment Variable: `VITE_API_URL=https://your-render-url.onrender.com`
4. Deploy!

---

## 📁 Project Structure

```
truthlayer/
├── backend/
│   ├── main.py              # FastAPI app + SSE streaming endpoint
│   ├── agents/
│   │   ├── extractor.py     # Gemini claim extraction agent
│   │   └── verifier.py      # Tavily + Gemini verification agent
│   ├── utils/
│   │   └── pdf_parser.py    # PyMuPDF text extraction
│   ├── requirements.txt
│   ├── render.yaml          # Render deployment config
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app with SSE state machine
│   │   ├── index.css        # Global design system
│   │   └── components/
│   │       ├── ClaimCard.jsx     # Individual claim result
│   │       ├── UploadZone.jsx    # Drag-and-drop PDF upload
│   │       ├── ProgressBar.jsx   # Real-time progress indicator
│   │       └── ResultsPanel.jsx  # Results with filters & stats
│   ├── vercel.json
│   └── .env.example
└── README.md
```

---

## 🎯 Evaluation Notes

This app is specifically designed to handle the **"Trap Document"** test:
- **Outdated Statistics** → Flagged as `Inaccurate` with the correct current figure provided
- **Hallucinated Facts** → Flagged as `False` with contradicting evidence cited
- **Correct Facts** → Confirmed as `Verified` with source links
- **Claims with no online footprint** → Marked `Unverifiable` with transparency

---

## 📄 License

MIT License — Built as part of Cog Culture Management Trainee Assessment.
