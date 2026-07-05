"""
summarizer.py
-------------
Summarizes lengthy contract text into plain, easy-to-understand language
using a Hugging Face transformer summarization model.

We use "facebook/bart-large-cnn" — a well-known, solid general-purpose
summarization model. It's not fine-tuned specifically on legal text
(a true production legal-AI tool would fine-tune on legal documents),
but it works well out of the box and is the honest, standard choice for
a project at this stage.

Note: transformer summarization models have an input length limit
(~1024 tokens for BART). For long contracts, we summarize chunk-by-chunk
and then combine, rather than feeding the whole document at once.
"""

from transformers import pipeline

MODEL_NAME = "facebook/bart-large-cnn"


class Summarizer:
    def __init__(self):
        print(f"Loading summarization model: {MODEL_NAME} (first run downloads it)...")
        self.summarizer = pipeline("summarization", model=MODEL_NAME)

    def summarize_chunk(self, text: str, max_length: int = 120, min_length: int = 30) -> str:
        """Summarize a single chunk of text (must be within the model's token limit)."""
        if len(text.split()) < 40:
            # Too short to meaningfully summarize — just return as-is
            return text

        result = self.summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
        )
        return result[0]["summary_text"]

    def summarize_document(self, chunks: list[dict]) -> str:
        """
        Summarize a full document by summarizing each chunk, then combining
        those chunk-summaries into one final summary.

        Args:
            chunks: output of chunker.chunk_text() — list of {"text": ..., ...}
        """
        chunk_summaries = []
        for chunk in chunks:
            summary = self.summarize_chunk(chunk["text"])
            chunk_summaries.append(summary)

        combined = " ".join(chunk_summaries)

        # If the combined chunk-summaries are still long, do one more pass
        if len(combined.split()) > 150:
            combined = self.summarize_chunk(combined, max_length=150, min_length=50)

        return combined


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from pdf_extractor import extract_text_from_pdf
    from chunker import chunk_text

    if len(sys.argv) < 2:
        print("Usage: python summarizer.py <path_to_pdf>")
        sys.exit(1)

    pages = extract_text_from_pdf(sys.argv[1])
    chunks = chunk_text(pages, chunk_size=200, overlap=30)

    summarizer = Summarizer()
    summary = summarizer.summarize_document(chunks)

    print("\n--- Plain-language summary ---")
    print(summary)
