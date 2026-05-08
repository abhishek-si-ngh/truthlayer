"""
Claim Extractor Agent — uses Ollama Cloud to identify verifiable factual claims
from document text.
"""

import os
import json
import re
from utils.ai_client import ai_client

def repair_json_list(s: str) -> str:
    # Remove markdown code fences
    s = re.sub(r"```json\s*", "", s)
    s = re.sub(r"```\s*", "", s)
    
    # Find the first [ and the last ]
    start = s.find('[')
    end = s.rfind(']')
    if start != -1 and end != -1:
        s = s[start:end+1]
    
    # Replace unescaped newlines
    s = s.replace('\n', ' ')
    
    # Fix trailing commas
    s = re.sub(r",\s*]", "]", s)
    s = re.sub(r",\s*}", "}", s)
    
    return s.strip()

EXTRACTION_PROMPT = """You are an expert fact-checking analyst. Your job is to extract ONLY specific, verifiable factual claims from the provided document text.

### EXAMPLE OUTPUT:
[
  {{
    "id": 1,
    "claim": "The global AI market reached $900 billion in 2024.",
    "context": "Market Statistics section",
    "category": "financial"
  }}
]

### DATA:
DOCUMENT TEXT:
{text}

### OUTPUT INSTRUCTIONS:
Return ONLY the JSON array. Do not include markdown code fences or explanation. Ensure all JSON strings are properly escaped.
"""

async def extract_claims(document_text: str) -> list[dict]:
    """
    Use AI to extract verifiable claims from document text.
    Returns a list of claim dictionaries.
    """
    # Truncate to ~30k chars for context safety
    truncated_text = document_text[:30000]
    prompt = EXTRACTION_PROMPT.format(text=truncated_text)

    try:
        raw = await ai_client.generate_completion(
            prompt=prompt,
            temperature=0.1,
            max_tokens=4096
        )
        raw = raw.strip()
    except Exception as e:
        print(f"Ollama extraction error: {e}")
        raise

    # Robust JSON extraction
    try:
        json_str = repair_json_list(raw)
        claims = json.loads(json_str)
    except Exception as e:
        print(f"JSON extraction error in extractor: {e}. Raw: {raw}")
        # Try to find all claim blocks with regex as fallback
        claims = []
        claim_texts = re.findall(r'"claim":\s*"([^"]+)"', raw)
        for i, text in enumerate(claim_texts):
            claims.append({
                "id": i + 1,
                "claim": text,
                "context": "Extracted via fallback parser",
                "category": "other"
            })
        
        if not claims:
            raise Exception(f"Failed to parse any claims from LLM response: {e}")

    # Validate structure
    validated = []
    if isinstance(claims, list):
        for i, c in enumerate(claims):
            if isinstance(c, dict):
                validated.append(
                    {
                        "id": c.get("id", i + 1),
                        "claim": str(c.get("claim", "")).strip(),
                        "context": str(c.get("context", "")).strip(),
                        "category": str(c.get("category", "other")).strip(),
                    }
                )
    
    return validated
