"""
qa_chatbot.py
-------------
RAG (Retrieval-Augmented Generation) chatbot: answers user questions
about the uploaded document by retrieving relevant chunks (via
VectorStore.search, from Week 1) and passing them to a Hugging Face
extractive QA model.

Why "extractive" QA and not a generative LLM?
Extractive QA models (like the one below) pull the answer directly from
the retrieved text, rather than generating new text. This is actually
safer and more honest for a legal document tool — the answer is always
traceable to an exact span in the source document, which matters a lot
when the topic is legal/contractual (you don't want a model "creatively"
answering questions about a contract).

Model used: "deepset/roberta-base-squad2" — a strong, widely-used
extractive QA model fine-tuned on SQuAD2 (a standard QA benchmark).
"""

from transformers import pipeline
from vector_store import VectorStore

QA_MODEL_NAME = "deepset/roberta-base-squad2"


class LegalChatbot:
    def __init__(self, vector_store: VectorStore = None):
        # Reuse an existing VectorStore instance if provided (avoids
        # reloading the embedding model twice), or create a new one.
        self.vector_store = vector_store or VectorStore()

        print(f"Loading QA model: {QA_MODEL_NAME} (first run downloads it)...")
        self.qa_pipeline = pipeline("question-answering", model=QA_MODEL_NAME)

    def ask(self, question: str, top_k: int = 3, doc_name: str = None) -> dict:
        """
        Answer a question about a specific uploaded document.

        Steps:
            1. Retrieve top_k relevant chunks via semantic search (Week 1 code),
               restricted to `doc_name` so multi-document uploads don't cross-contaminate
            2. Concatenate them into one context string
            3. Run extractive QA on that context to find the exact answer span

        Returns:
            {
                "answer": "...",
                "confidence": 0.87,
                "source_page": 2,
                "context_used": "..."   # the retrieved text the answer came from
            }
        """
        retrieved_chunks = self.vector_store.search(question, top_k=top_k, doc_name=doc_name)

        if not retrieved_chunks:
            return {
                "answer": "No relevant information found in the uploaded document.",
                "confidence": 0.0,
                "source_page": None,
                "context_used": "",
            }

        # Combine retrieved chunks into one context block for the QA model
        context = " ".join(chunk["text"] for chunk in retrieved_chunks)

        result = self.qa_pipeline(question=question, context=context)

        # Report which page the best-matching chunk came from, so the user
        # can go verify it themselves — important for a legal-document tool
        best_chunk = retrieved_chunks[0]

        return {
            "answer": result["answer"],
            "confidence": round(result["score"], 3),
            "source_page": best_chunk["page"],
            "context_used": context[:400],  # trimmed for display
        }


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from pdf_extractor import extract_text_from_pdf
    from chunker import chunk_text

    if len(sys.argv) < 2:
        print("Usage: python qa_chatbot.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    doc_name = pdf_path.split("/")[-1].replace(".pdf", "")

    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(pages, chunk_size=150, overlap=30)

    store = VectorStore()
    store.add_chunks(chunks, doc_name=doc_name)

    bot = LegalChatbot(vector_store=store)

    print("\nAsk questions about the document (type 'quit' to exit):")
    while True:
        question = input("\nYou: ")
        if question.lower() == "quit":
            break
        result = bot.ask(question, doc_name=doc_name)
        print(f"Bot: {result['answer']}  (confidence: {result['confidence']}, page {result['source_page']})")
