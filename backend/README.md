# ⚙️ TruthLayer Backend

The FastAPI-based backend for **TruthLayer**, an AI-powered fact-checking engine. This service handles PDF parsing, claim extraction using various LLMs, and real-time verification using the Tavily Search API.

## 🚀 Features

- **Asynchronous Processing**: Uses `asyncio` for non-blocking operations.
- **Real-time Streaming**: Implements Server-Sent Events (SSE) to stream verification results to the client.
- **AI Fallback Chain**: Robust AI client that rotates through Groq, Gemini, and Ollama to ensure high availability.
- **Live Web Verification**: Integrates with Tavily Search API to fetch the latest evidence from the web.
- **PDF Extraction**: Efficiently extracts text from PDF documents using PyMuPDF.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/) / [Gunicorn](https://gunicorn.org/)
- **PDF Parsing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **AI Clients**: Groq SDK, Google Generative AI, Ollama
- **Search**: [Tavily API](https://tavily.com/)
- **Environment**: Python 3.11+

## 📁 Structure

- `main.py`: Entry point for the FastAPI application and SSE logic.
- `agents/`:
  - `extractor.py`: Logic for identifying verifiable claims from text.
  - `verifier.py`: Logic for searching evidence and adjudicating claims.
- `utils/`:
  - `ai_client.py`: Multi-provider LLM handler with fallback logic.
  - `pdf_parser.py`: PDF text extraction utility.
  - Provider-specific clients (`groq_client.py`, `gemini_client.py`, etc.).

## 🔧 Local Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file based on `.env.example`:
   ```env
   GROQ_API_KEY=...
   GEMINI_API_KEYS=...
   TAVILY_API_KEY=...
   ALLOWED_ORIGINS=http://localhost:5173
   ```

4. **Run Server**:
   ```bash
   uvicorn main.py:app --reload --port 8000
   ```

## 🚢 Deployment

The backend is configured for deployment on **Render** via `render.yaml`.
- Uses `Gunicorn` with `UvicornWorker` for production-grade performance.
- Ensure all API keys are set as Environment Variables in the Render dashboard.
