"""
pdf_extractor.py
-----------------
Handles extracting raw text from an uploaded resume PDF.

Works with:
    - A Streamlit UploadedFile object (what st.file_uploader() returns)
    - A regular file path (str)
    - A file-like object opened in binary mode

Design goal: never crash the app, even with:
    - Empty PDFs
    - Pages that have no extractable text (e.g. scanned images)
    - Corrupted/unreadable PDFs
"""

import pdfplumber


def extract_text_from_pdf(pdf_file):
    """
    Accepts a Streamlit UploadedFile OR a file-like object OR a file path (str).

    Returns:
        str - extracted resume text. Returns an empty string "" if
        extraction fails or no text is found, instead of raising an
        exception (so the app doesn't crash).
    """
    extracted_text_parts = []

    try:
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) == 0:
                # Empty PDF (no pages at all)
                return ""

            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:  # page.extract_text() can return None
                        extracted_text_parts.append(page_text)
                except Exception:
                    # If a single page fails to extract, skip it and
                    # keep going instead of crashing the whole app.
                    continue

    except Exception as e:
        # Covers corrupted files, unsupported formats, permission issues, etc.
        print(f"[pdf_extractor] Failed to read PDF: {e}")
        return ""

    full_text = "\n".join(extracted_text_parts).strip()
    return full_text


# ---------------------------------------------------------------------------
# Quick manual test (only runs if you execute this file directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        text = extract_text_from_pdf(path)
        print("----- EXTRACTED TEXT -----")
        print(text if text else "(No text extracted)")
    else:
        print("Usage: python pdf_extractor.py <path_to_pdf>")
