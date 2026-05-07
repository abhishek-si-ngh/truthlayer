"""
PDF Parser utility — extracts text from uploaded PDF files using PyMuPDF.
Handles multi-page PDFs and returns clean, normalized text.
"""

import fitz  # PyMuPDF
import re


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract raw text from a PDF given its bytes.
    Returns a single string with all pages concatenated.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages_text.append(f"[Page {page_num + 1}]\n{text.strip()}")

    doc.close()

    full_text = "\n\n".join(pages_text)
    # Normalize excessive whitespace while preserving paragraph breaks
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)
    full_text = re.sub(r" {2,}", " ", full_text)

    return full_text.strip()
