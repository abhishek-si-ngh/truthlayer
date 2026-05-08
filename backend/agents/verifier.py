"""
Fact Verifier Agent — searches the live web via Tavily and adjudicates
each claim using Ollama as the reasoning engine.
"""

import os
import json
import re
import asyncio
from tavily import TavilyClient
from utils.ai_client import ai_client

# Initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

def repair_json(s: str) -> str:
    """
    Aggressive JSON repair for common LLM mistakes.
    """
    # Remove markdown blocks
    s = re.sub(r"```json\s*", "", s)
    s = re.sub(r"```\s*", "", s)
    
    # Extract the block between the first { and last }
    start = s.find('{')
    end = s.rfind('}')
    if start != -1 and end != -1:
        s = s[start:end+1]
    
    # Replace unescaped newlines inside strings
    # This looks for newlines that are not preceded by a comma or followed by a quote/brace
    s = s.replace('\n', ' ')
    
    # Fix trailing commas before closing braces
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*]", "]", s)
    
    return s.strip()

ADJUDICATION_PROMPT = """You are a rigorous fact-checking adjudicator. Given a CLAIM and EVIDENCE retrieved from the live web, your job is to deliver a precise verdict.

### TASK:
1. Analyze the CLAIM against the EVIDENCE.
2. Determine the verdict (Verified, Inaccurate, False, or Unverifiable).
3. Provide a concise explanation.

### EXAMPLES OF VALID OUTPUT:
{{
  "verdict": "Verified",
  "confidence": 0.95,
  "explanation": "Multiple sources confirm the figure matches the latest report.",
  "correction": null,
  "sources": ["https://source1.com"]
}}

### DATA:
CLAIM: {claim}

RETRIEVED EVIDENCE:
{evidence}

### OUTPUT INSTRUCTIONS:
Return ONLY the JSON object. Do not include markdown code fences. Ensure all quotes are properly closed.
"""

async def verify_claim(claim: dict) -> dict:
    """
    Verify a single claim against live web data.
    Returns an enriched claim dict with verdict, explanation, correction, sources.
    """
    claim_text = claim["claim"]

    # Step 1: Search the web via Tavily
    try:
        if not tavily_client:
            raise Exception("TAVILY_API_KEY not found in environment")

        # Use asyncio.to_thread for the sync Tavily SDK call
        search_results = await asyncio.to_thread(
            tavily_client.search,
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

    # Step 2: Adjudicate with AI
    try:
        prompt = ADJUDICATION_PROMPT.format(
            claim=claim_text,
            evidence=evidence_text[:5000],
        )

        raw = await ai_client.generate_completion(
            prompt=prompt,
            temperature=0.0,
            max_tokens=1024
        )
        raw = raw.strip()

        try:
            json_str = repair_json(raw)
            adjudication = json.loads(json_str)
        except Exception as e:
            # Last ditch effort: simple regex extraction for values
            print(f"JSON repair failed: {e}. Raw: {raw}")
            # Try to extract at least the verdict if everything else fails
            verdict_match = re.search(r'"verdict":\s*"([^"]+)"', raw)
            verdict = verdict_match.group(1) if verdict_match else "Unverifiable"
            
            adjudication = {
                "verdict": verdict,
                "confidence": 0.5,
                "explanation": "Parsing error occurred, but extracted verdict from raw text.",
                "correction": None,
                "sources": source_urls,
            }

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
