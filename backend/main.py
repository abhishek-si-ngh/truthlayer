"""
TruthLayer — FastAPI Backend
Real-time fact-checking via Server-Sent Events (SSE)
"""

import os
import json
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
load_dotenv()

from utils.pdf_parser import extract_text_from_pdf
from agents.extractor import extract_claims
from agents.verifier import verify_claim

app = FastAPI(
    title="TruthLayer API",
    description="Automated fact-checking engine for PDF documents",
    version="1.0.0",
)

# CORS — allow frontend origins
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "service": "TruthLayer API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


async def fact_check_stream(file_bytes: bytes, filename: str):
    """
    Generator that streams SSE events for each stage of the pipeline:
    1. PDF parsed
    2. Claims extracted (sends all claims)
    3. Each claim verified one-by-one (real-time updates)
    4. Done
    """

    def send_event(event_type: str, data: dict) -> str:
        payload = json.dumps({"type": event_type, **data})
        return f"data: {payload}\n\n"

    try:
        # Stage 1 — Parse PDF
        yield send_event("status", {"message": "📄 Parsing PDF document...", "stage": "parsing"})
        await asyncio.sleep(0)

        try:
            text = extract_text_from_pdf(file_bytes)
        except Exception as e:
            yield send_event("error", {"message": f"Failed to parse PDF: {str(e)}"})
            return

        word_count = len(text.split())
        yield send_event(
            "parsed",
            {
                "message": f"✅ PDF parsed successfully — {word_count:,} words extracted",
                "word_count": word_count,
                "filename": filename,
            },
        )
        await asyncio.sleep(0)

        # Stage 2 — Extract Claims
        yield send_event("status", {"message": "🔍 Extracting verifiable claims with AI...", "stage": "extracting"})
        await asyncio.sleep(0)

        try:
            claims = await extract_claims(text)
        except Exception as e:
            yield send_event("error", {"message": f"Claim extraction failed: {str(e)}"})
            return

        if not claims:
            yield send_event("error", {"message": "No verifiable claims found in this document."})
            return

        yield send_event(
            "claims_extracted",
            {
                "message": f"🎯 Found {len(claims)} verifiable claims — starting verification...",
                "total": len(claims),
                "claims": claims,
            },
        )
        await asyncio.sleep(0)

        # Stage 3 — Verify each claim
        results = []
        for i, claim in enumerate(claims):
            yield send_event(
                "verifying",
                {
                    "message": f"🔎 Verifying claim {i + 1}/{len(claims)}...",
                    "current": i + 1,
                    "total": len(claims),
                    "claim_id": claim["id"],
                },
            )
            await asyncio.sleep(0)

            try:
                result = await verify_claim(claim)
            except Exception as e:
                result = {
                    **claim,
                    "verdict": "Unverifiable",
                    "confidence": 0.0,
                    "explanation": f"Verification error: {str(e)}",
                    "correction": None,
                    "sources": [],
                }

            results.append(result)

            yield send_event(
                "claim_result",
                {
                    "claim": result,
                    "current": i + 1,
                    "total": len(claims),
                },
            )
            await asyncio.sleep(0)

        # Stage 4 — Summary
        verdict_counts = {}
        for r in results:
            v = r["verdict"]
            verdict_counts[v] = verdict_counts.get(v, 0) + 1

        yield send_event(
            "done",
            {
                "message": "✅ Fact-check complete!",
                "summary": verdict_counts,
                "total": len(results),
                "results": results,
            },
        )

    except Exception as e:
        yield send_event("error", {"message": f"Unexpected error: {str(e)}"})


@app.post("/api/fact-check")
async def fact_check(file: UploadFile = File(...)):
    """
    Upload a PDF and receive real-time fact-checking results via SSE.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    max_size = 10 * 1024 * 1024  # 10 MB
    file_bytes = await file.read()

    if len(file_bytes) > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    return StreamingResponse(
        fact_check_stream(file_bytes, file.filename),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
