"""
Claim Extractor Agent — uses Google Gemini to identify verifiable factual claims
from document text. Filters out opinions and subjective statements.
"""

import os
import json
import re
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

EXTRACTION_PROMPT = """You are an expert fact-checking analyst. Your job is to extract ONLY specific, verifiable factual claims from the provided document text.

RULES:
- Extract claims that contain: statistics, percentages, dates, financial figures, technical metrics, named entity facts, scientific data, market figures, rankings, or any concrete numerical/temporal assertions.
- IGNORE: opinions, predictions, metaphors, marketing language without specific numbers, subjective statements.
- Each claim must be a self-contained sentence that can be independently verified.
- Extract between 5 and 20 claims depending on document length.
- Focus on claims that are most likely to be outdated, exaggerated, or hallucinated.

OUTPUT FORMAT (strict JSON array, no markdown fences):
[
  {
    "id": 1,
    "claim": "The exact claim text from the document",
    "context": "Brief surrounding context (1 sentence)",
    "category": "statistic|date|financial|technical|scientific|other"
  },
  ...
]

DOCUMENT TEXT:
{text}

Return ONLY the JSON array. No explanation, no markdown."""


def extract_claims(document_text: str) -> list[dict]:
    """
    Use Gemini to extract verifiable claims from document text.
    Returns a list of claim dictionaries.
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=8192,
        ),
    )

    # Truncate to ~50k chars to stay within context limits
    truncated_text = document_text[:50000]

    prompt = EXTRACTION_PROMPT.format(text=truncated_text)

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    claims = json.loads(raw)

    # Validate structure
    validated = []
    for i, c in enumerate(claims):
        validated.append(
            {
                "id": c.get("id", i + 1),
                "claim": str(c.get("claim", "")).strip(),
                "context": str(c.get("context", "")).strip(),
                "category": str(c.get("category", "other")).strip(),
            }
        )

    return validated
