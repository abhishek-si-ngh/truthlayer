================================================================================
  TRUTHLAYER — AI-Powered Fact-Checking Engine
  Cog Culture Management Trainee Assessment | Part 2
================================================================================

LIVE APP    : https://truthlayer.vercel.app
BACKEND API : https://truthlayer-api.onrender.com
GITHUB REPO : https://github.com/abhishek-si-ngh/truthlayer

--------------------------------------------------------------------------------
WHAT IT DOES
--------------------------------------------------------------------------------

TruthLayer is an automated fact-checking web application. You upload any PDF
document; the system:
  1. Extracts all verifiable claims (statistics, dates, financial/technical figures)
  2. Searches the live web for evidence via Tavily Search API
  3. Uses an AI model to adjudicate each claim and assign a verdict
  4. Streams results back to your browser in real time (no page refresh needed)

Verdict Types:
  [V]  Verified      - Claim is supported by live web evidence
  [I]  Inaccurate    - Claim contains outdated or wrong figures (correction given)
  [F]  False         - Claim directly contradicts credible web sources
  [U]  Unverifiable  - Insufficient evidence found online

--------------------------------------------------------------------------------
TECH STACK
--------------------------------------------------------------------------------

  Frontend    : React 18 + Vite  (deployed on Vercel)
  Backend     : Python 3.11, FastAPI, Uvicorn/Gunicorn  (deployed on Render)
  PDF Parser  : PyMuPDF (fitz)
  AI Models   : Groq (primary) -> Gemini 1.5 Flash -> Ollama (fallback chain)
  Web Search  : Tavily Search API (advanced mode, 5 sources per claim)
  Streaming   : Server-Sent Events (SSE) for real-time claim updates

--------------------------------------------------------------------------------
LOCAL SETUP — QUICK START
--------------------------------------------------------------------------------

REQUIREMENTS:
  - Python 3.11 or higher
  - Node.js 18 or higher
  - At least one AI API key (Groq, Gemini, or Ollama)
  - Tavily API key

STEP 1 — Clone the repository:
  git clone https://github.com/abhishek-si-ngh/truthlayer.git
  cd truthlayer

STEP 2 — Backend:
  cd backend
  python -m venv venv
  venv\Scripts\activate           (Windows)
  source venv/bin/activate        (macOS / Linux)
  pip install -r requirements.txt
  copy .env.example .env
  [Edit .env and add your API keys — see section below]
  uvicorn main:app --reload --port 8000

STEP 3 — Frontend:
  cd frontend
  npm install
  echo VITE_API_URL=http://localhost:8000 > .env.local
  npm run dev
  [Open http://localhost:5173 in your browser]

--------------------------------------------------------------------------------
ENVIRONMENT VARIABLES (backend/.env)
--------------------------------------------------------------------------------

  GROQ_API_KEY=your_groq_key_here
  GEMINI_API_KEYS=key1,key2        <- comma-separated for rotation
  TAVILY_API_KEY=your_tavily_key
  DEMO_MODE=false                  <- set to true for UI testing without keys
  ALLOWED_ORIGINS=http://localhost:5173

Where to get free API keys:
  Groq    : https://console.groq.com     (generous free tier)
  Gemini  : https://aistudio.google.com  (free tier)
  Tavily  : https://tavily.com           (1,000 searches/month free)

--------------------------------------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------------------------------------

  truthlayer/
  +-- backend/
  |   +-- main.py                  FastAPI app + SSE streaming endpoint
  |   +-- agents/
  |   |   +-- extractor.py         AI claim extraction agent
  |   |   +-- verifier.py          Tavily + AI verification agent
  |   +-- utils/
  |   |   +-- ai_client.py         Unified AI client (Groq->Gemini->Ollama)
  |   |   +-- gemini_client.py     Gemini key-rotation client
  |   |   +-- groq_client.py       Groq API client
  |   |   +-- ollama_client.py     Ollama Cloud API client
  |   |   +-- pdf_parser.py        PyMuPDF text extraction
  |   +-- requirements.txt
  |   +-- render.yaml
  |   +-- .env.example
  +-- frontend/
  |   +-- src/
  |   |   +-- App.jsx              Main app with SSE state machine
  |   |   +-- index.css            Global design system
  |   |   +-- components/
  |   |       +-- ClaimCard.jsx    Claim result with verdict badge
  |   |       +-- UploadZone.jsx   Drag-and-drop PDF upload
  |   |       +-- ProgressBar.jsx  Real-time progress indicator
  |   |       +-- ResultsPanel.jsx Results with filters & summary stats
  |   +-- index.html
  |   +-- vite.config.js
  |   +-- vercel.json
  +-- render.yaml
  +-- README.md
  +-- README.txt

--------------------------------------------------------------------------------
DEPLOYMENT
--------------------------------------------------------------------------------

Backend (Render):
  - Root Directory : backend
  - Build          : pip install -r requirements.txt
  - Start          : gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app
                     --bind 0.0.0.0:$PORT
  - Env vars       : GROQ_API_KEY, GEMINI_API_KEYS, TAVILY_API_KEY,
                     ALLOWED_ORIGINS, DEMO_MODE

Frontend (Vercel):
  - Root Directory : frontend
  - Framework      : Vite
  - Env vars       : VITE_API_URL=https://truthlayer-api.onrender.com

--------------------------------------------------------------------------------
EVALUATION — "TRAP DOCUMENT" TEST
--------------------------------------------------------------------------------

  Outdated stats     -> Flagged INACCURATE with the correct current figure
  Hallucinated facts -> Flagged FALSE with contradicting evidence cited
  Correct facts      -> Confirmed VERIFIED with source URLs
  No web footprint   -> Marked UNVERIFIABLE transparently

--------------------------------------------------------------------------------
LICENSE
--------------------------------------------------------------------------------

MIT License
Built by Abhishek Singh as part of the Cog Culture Management Trainee Assessment.

================================================================================
