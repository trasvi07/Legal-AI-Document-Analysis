"""
pdf_extractor.py
----------------
Extracts raw text from a PDF file using PyMuPDF (fitz).

Legal documents often have multiple pages, headers/footers, and
inconsistent spacing. This module extracts text page-by-page and
keeps track of which page each chunk of text came from, since you'll
want to cite "this clause was found on page 4" later in the RAG chatbot.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF, page by page.

    Returns a list of dicts like:
        [{"page": 1, "text": "..."}, {"page": 2, "text": "..."}, ...]

    Why page-by-page and not one giant string?
    - Keeps page numbers for citations later ("see page 3")
    - Makes chunking easier/more accurate downstream
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")  # plain text extraction
        text = text.strip()

        if text:  # skip totally blank pages
            pages.append({"page": page_num, "text": text})

    doc.close()
    return pages


def extract_full_text(pdf_path: str) -> str:
    """
    Convenience function: returns the entire document as one string,
    with page breaks marked. Useful for quick debugging/printing.
    """
    pages = extract_text_from_pdf(pdf_path)
    full_text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)
    return full_text


if __name__ == "__main__":
    # Quick manual test — run this file directly to sanity check extraction
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path_to_pdf>")
        sys.exit(1)

    path = sys.argv[1]
    pages = extract_text_from_pdf(path)

    print(f"Extracted {len(pages)} non-empty pages.\n")
    for p in pages[:2]:  # print first 2 pages as a preview
        print(f"--- Page {p['page']} (first 300 chars) ---")
        print(p["text"][:300])
        print()
