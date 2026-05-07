"""
Fact Verifier Agent — searches the live web via Tavily and adjudicates
each claim using Gemini as the reasoning engine.
"""

import os
import json
import re
import google.generativeai as genai
from tavily import TavilyClient

# Configure clients
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

ADJUDICATION_PROMPT = """You are a rigorous fact-checking adjudicator. Given a CLAIM and EVIDENCE retrieved from the live web, your job is to deliver a precise verdict.

CLAIM: {claim}

RETRIEVED EVIDENCE:
{evidence}

VERDICT RULES:
- "Verified": The claim is clearly supported by at least one credible source in the evidence. The data matches within reasonable tolerance.
- "Inaccurate": The claim has a factual error or contains outdated data. A more accurate figure or date exists in the evidence.
- "False": The claim directly contradicts credible evidence with no supporting data found.
- "Unverifiable": Insufficient evidence found; the claim cannot be confirmed or denied with available sources.

OUTPUT FORMAT (strict JSON, no markdown):
{{
  "verdict": "Verified|Inaccurate|False|Unverifiable",
  "confidence": 0.0-1.0,
  "explanation": "Clear, concise explanation (2-3 sentences max) of WHY this verdict was reached.",
  "correction": "If Inaccurate or False: the correct fact with its source. Otherwise: null.",
  "sources": ["url1", "url2"]
}}

Return ONLY the JSON object."""


def verify_claim(claim: dict) -> dict:
    """
    Verify a single claim against live web data.
    Returns an enriched claim dict with verdict, explanation, correction, sources.
    """
    claim_text = claim["claim"]

    # Step 1: Search the web via Tavily
    try:
        search_results = tavily_client.search(
            query=claim_text,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )
        evidence_parts = []

        if search_results.get("answer"):
            evidence_parts.append(f"Summary: {search_results['answer']}")

        for result in search_results.get("results", []):
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")[:600]
            evidence_parts.append(f"Source [{url}] — {title}:\n{content}")

        evidence_text = "\n\n".join(evidence_parts) if evidence_parts else "No relevant results found."
        source_urls = [r.get("url", "") for r in search_results.get("results", [])]

    except Exception as e:
        evidence_text = f"Search failed: {str(e)}"
        source_urls = []

    # Step 2: Adjudicate with Gemini
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=1024,
            ),
        )

        prompt = ADJUDICATION_PROMPT.format(
            claim=claim_text,
            evidence=evidence_text[:6000],
        )

        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        adjudication = json.loads(raw)

    except Exception as e:
        adjudication = {
            "verdict": "Unverifiable",
            "confidence": 0.0,
            "explanation": f"Adjudication error: {str(e)}",
            "correction": None,
            "sources": source_urls,
        }

    return {
        **claim,
        "verdict": adjudication.get("verdict", "Unverifiable"),
        "confidence": float(adjudication.get("confidence", 0.0)),
        "explanation": adjudication.get("explanation", ""),
        "correction": adjudication.get("correction"),
        "sources": adjudication.get("sources", source_urls),
    }
