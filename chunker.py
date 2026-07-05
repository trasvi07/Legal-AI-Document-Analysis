"""
chunker.py
----------
Splits extracted page text into overlapping chunks suitable for embedding.

Why chunk at all?
Embedding models have a token limit, and semantic search works better on
smaller, focused pieces of text (e.g., one clause) rather than a whole
5-page contract. If we embedded the whole document as one vector, a
question about "termination" would get diluted by unrelated text about
"payment" in the same vector.

Why overlap?
Legal clauses sometimes span a chunk boundary. Overlapping chunks
(e.g., last 50 words of chunk N repeated at the start of chunk N+1)
reduces the chance that a clause gets awkwardly split in half with
no chunk containing the full meaning.
"""


def chunk_text(pages: list[dict], chunk_size: int = 200, overlap: int = 40) -> list[dict]:
    """
    Split page-level text into overlapping word-based chunks.

    Args:
        pages: output of pdf_extractor.extract_text_from_pdf()
               i.e. [{"page": 1, "text": "..."}, ...]
        chunk_size: target number of words per chunk
        overlap: number of words repeated between consecutive chunks

    Returns:
        A list of chunk dicts:
        [{"chunk_id": 0, "page": 1, "text": "..."}, ...]
    """
    chunks = []
    chunk_id = 0

    for page in pages:
        words = page["text"].split()
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text_str = " ".join(chunk_words)

            chunks.append({
                "chunk_id": chunk_id,
                "page": page["page"],
                "text": chunk_text_str,
            })
            chunk_id += 1

            if end >= len(words):
                break
            start = end - overlap  # step back by `overlap` words for the next chunk

    return chunks


if __name__ == "__main__":
    # Quick manual test
    from pdf_extractor import extract_text_from_pdf
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chunker.py <path_to_pdf>")
        sys.exit(1)

    pages = extract_text_from_pdf(sys.argv[1])
    chunks = chunk_text(pages, chunk_size=40, overlap=10)  # small size for demo visibility

    print(f"Created {len(chunks)} chunks from {len(pages)} pages.\n")
    for c in chunks:
        print(f"[chunk {c['chunk_id']} | page {c['page']}] {c['text'][:120]}...")
        print()
