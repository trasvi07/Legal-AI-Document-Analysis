"""
vector_store.py
----------------
Embeds text chunks using Sentence Transformers and stores them in ChromaDB
for semantic search.

Flow:
    text chunks -> embedding model -> vectors -> stored in ChromaDB
    (later) user question -> embedding -> ChromaDB similarity search -> top chunks

We use "all-MiniLM-L6-v2" — a small, fast Sentence Transformers model.
It's not the most powerful embedding model out there, but it's a good
starting point: ~80MB, runs fine on CPU, and is the standard "hello world"
model for semantic search projects. You can swap it for a stronger model
later (e.g., "all-mpnet-base-v2") once the pipeline works end-to-end.
"""

import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "./data/chroma_store"       # local, persistent on-disk storage
COLLECTION_NAME = "legal_documents"


class VectorStore:
    def __init__(self):
        print(f"Loading embedding model: {MODEL_NAME} (first run downloads it, ~80MB)...")
        self.model = SentenceTransformer(MODEL_NAME)

        # PersistentClient saves data to disk so you don't lose it between runs
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def add_chunks(self, chunks: list[dict], doc_name: str):
        """
        Embed and store a list of chunks (from chunker.chunk_text).

        Each chunk gets a unique ID so multiple documents can share one
        ChromaDB collection without ID collisions.
        """
        texts = [c["text"] for c in chunks]
        ids = [f"{doc_name}_chunk_{c['chunk_id']}" for c in chunks]
        metadatas = [{"page": c["page"], "doc_name": doc_name} for c in chunks]

        embeddings = self.model.encode(texts, show_progress_bar=True).tolist()

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        print(f"Stored {len(chunks)} chunks from '{doc_name}' into ChromaDB.")

    def search(self, query: str, top_k: int = 3, doc_name: str = None) -> list[dict]:
        """
        Embed a user query and retrieve the top_k most semantically
        similar chunks from ChromaDB.

        Args:
            doc_name: if provided, restricts search to chunks from that
                      specific document only. Without this, a query would
                      search across ALL documents ever uploaded, which is
                      wrong once more than one document is in the store.
        """
        query_embedding = self.model.encode([query]).tolist()
        where_filter = {"doc_name": doc_name} if doc_name else None

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=where_filter,
        )

        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "text": results["documents"][0][i],
                "page": results["metadatas"][0][i]["page"],
                "doc_name": results["metadatas"][0][i]["doc_name"],
                "distance": results["distances"][0][i],  # lower = more similar
            })
        return hits


if __name__ == "__main__":
    # End-to-end manual test: extract -> chunk -> embed -> store -> search
    import sys
    from pdf_extractor import extract_text_from_pdf
    from chunker import chunk_text

    if len(sys.argv) < 2:
        print("Usage: python vector_store.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    doc_name = pdf_path.split("/")[-1].replace(".pdf", "")

    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(pages, chunk_size=150, overlap=30)

    store = VectorStore()
    store.add_chunks(chunks, doc_name=doc_name)

    print("\n--- Test query ---")
    query = "What happens if I pay rent late?"
    results = store.search(query, top_k=2)

    print(f"Query: {query}\n")
    for r in results:
        print(f"[page {r['page']} | distance {r['distance']:.3f}] {r['text'][:200]}...")
        print()
