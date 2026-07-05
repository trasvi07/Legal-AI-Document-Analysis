# ⚖️ Legal AI – AI-Powered Legal Document Analysis Platform

An AI-powered full-stack NLP application that extracts, summarizes, and analyzes legal contracts using Retrieval-Augmented Generation (RAG), transformer models, and semantic search.

Upload a legal PDF and receive:

- 📄 Plain-language contract summary
- 🏷 Clause classification
- ⚠️ Risky clause detection
- 💬 AI-powered document question answering
- 🔍 Semantic search over contract content

---

# Features

- PDF text extraction using **PyMuPDF**
- Intelligent text chunking with overlap
- Semantic search using **Sentence Transformers + ChromaDB**
- Transformer-based contract summarization
- Clause classification into:
  - Payment
  - Confidentiality
  - Liability
  - Termination
- Rule-based risk detection
- Retrieval-Augmented Generation (RAG) chatbot
- REST API using FastAPI
- Interactive web interface using Streamlit

---

# Tech Stack

| Category | Technologies |
|-----------|--------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| NLP | Hugging Face Transformers, spaCy |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| PDF Processing | PyMuPDF |
| Language | Python |

---

# Project Architecture

```
                    PDF Upload
                         │
                         ▼
                 PDF Text Extraction
                    (PyMuPDF)
                         │
                         ▼
                Text Chunking Module
                         │
                         ▼
              Sentence Transformer
                   Embeddings
                         │
                         ▼
                   ChromaDB
                Vector Database
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        ▼                ▼                 ▼
 Summarization   Clause Classification   Risk Detection
        │
        ▼
    RAG Chatbot
        │
        ▼
     FastAPI Backend
        │
        ▼
   Streamlit Frontend
```

---

# Project Structure

```
Legal-AI-Document-Analysis/
│
├── main.py
├── pdf_extractor.py
├── chunker.py
├── vector_store.py
├── summarizer.py
├── clause_classifier.py
├── risk_detector.py
├── qa_chatbot.py
├── streamlit_app.py
│
├── sample_rental_agreement.pdf
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/trasvi07/Legal-AI-Document-Analysis.git

cd Legal-AI-Document-Analysis
```

Create a virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Download the spaCy English model

```bash
python -m spacy download en_core_web_sm
```

---

# Running the Backend

```bash
uvicorn main:app
```

Open

```
http://127.0.0.1:8000/docs
```

to access the FastAPI Swagger documentation.

---

# Running the Frontend

Open another terminal

```bash
streamlit run streamlit_app.py
```

Open

```
http://localhost:8501
```

---

# Usage

1. Upload a legal PDF.
2. The application extracts text.
3. Creates semantic embeddings.
4. Generates a plain-language summary.
5. Detects important clauses.
6. Flags risky contract terms.
7. Ask questions about the document using the AI chatbot.

---

# API Endpoints

| Endpoint | Description |
|-----------|-------------|
| POST /upload | Upload a document |
| GET /summary/{doc_id} | Generate summary |
| GET /clauses/{doc_id} | Classify clauses |
| GET /risks/{doc_id} | Detect risky clauses |
| POST /chat | Ask questions about the uploaded document |

---

# Example Workflow

```
Upload PDF
      │
      ▼
Extract Text
      │
      ▼
Create Chunks
      │
      ▼
Generate Embeddings
      │
      ▼
Store in ChromaDB
      │
      ▼
Summary
Clause Detection
Risk Detection
Chatbot
```

---

# Future Improvements

- OCR support for scanned PDFs
- Multi-document search
- Legal entity recognition
- Contract comparison
- Clause highlighting inside PDF
- Docker deployment
- Authentication system

---

# Screenshots

Add screenshots here after running the application.
<img width="882" height="410" alt="image" src="https://github.com/user-attachments/assets/b254ec29-2ebb-46c6-a628-4054570d7674" />

summary.png
<img width="884" height="440" alt="image" src="https://github.com/user-attachments/assets/c20b55fc-d4dc-4b62-a2e5-d179f49e6dbd" />

clauses.png
<img width="907" height="404" alt="image" src="https://github.com/user-attachments/assets/ac86fdfa-a5b6-4613-83f9-617ac7ffb017" />

Risk flag.png
<img width="858" height="374" alt="image" src="https://github.com/user-attachments/assets/8b5784a3-36ef-4500-963d-c1fb3ebe4f6e" />

chatbot.png
<img width="929" height="348" alt="image" src="https://github.com/user-attachments/assets/2ab7d5d7-c412-4a54-8aed-479ea93b6647" />


---

# License

MIT License
