# Legal AI — AI-Powered Legal Document Analysis Platform

A full-stack NLP platform that extracts, summarizes, and analyzes legal
contracts. Upload a PDF and get: a plain-language summary, clause
classification (payment/confidentiality/liability/termination), risky
term detection with explanations, and a RAG chatbot to ask questions
about the document.

## Architecture

```
PDF Upload
   |
   v
pdf_extractor.py  --> extracts text page-by-page (PyMuPDF)
   |
   v
chunker.py        --> splits into overlapping chunks
   |
   v
vector_store.py   --> embeds chunks (Sentence Transformers) + stores in ChromaDB
   |
   +--> summarizer.py        --> plain-language summary (Hugging Face BART)
   +--> clause_classifier.py --> clause classification (spaCy + keyword rules)
   +--> risk_detector.py     --> risky term flagging (pattern matching)
   +--> qa_chatbot.py        --> RAG chatbot (ChromaDB retrieval + HF QA model)
   |
   v
main.py (FastAPI)  --> exposes everything as a REST API
   |
   v
streamlit_app.py   --> user-facing web UI
```

## What I tested vs. what you'll test

I ran and confirmed working, in a sandboxed environment:
- `pdf_extractor.py` — extracted the sample rental agreement correctly
- `chunker.py` — confirmed correct overlapping chunk behavior
- `clause_classifier.py` — classification logic confirmed correct (tested
  the keyword-matching logic directly; the real run uses spaCy's
  `en_core_web_sm` model for sentence splitting, which I couldn't download
  in my sandbox — see setup step 4 below)
- `risk_detector.py` — confirmed correctly flags risky phrases with explanations

I could **not** test in my sandbox (no internet access to Hugging Face /
model hosting from there), so **you'll be running these for the first time**:
- `vector_store.py`'s embedding step (downloads a ~80MB model)
- `summarizer.py` (downloads `facebook/bart-large-cnn`, ~1.6GB)
- `qa_chatbot.py` (downloads `deepset/roberta-base-squad2`, ~500MB)
- The full FastAPI + Streamlit app running together

The logic in all of these is standard and written carefully, but since
I couldn't run them end-to-end myself, budget some time for debugging if
something doesn't work first try — that's normal for a project this size,
not a sign something is fundamentally wrong.

## Setup

1. **Python 3.10+ required.**

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Note: `torch` and `transformers` are large installs — this may take
   several minutes depending on your internet speed.

4. **Download the spaCy English model (one-time):**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the backend API:**
   ```bash
   cd app
   uvicorn main:app --reload
   ```
   First startup will download the embedding, summarization, and QA
   models (~2GB total) — this only happens once, then they're cached
   locally. Wait for "All models loaded. API ready." before moving on.

   Visit `http://127.0.0.1:8000/docs` to see interactive API documentation
   and test endpoints directly.

6. **Run the frontend (in a new terminal, same venv activated):**
   ```bash
   cd app
   streamlit run streamlit_app.py
   ```
   This opens a browser tab. Upload the sample PDF in `sample_docs/` or
   any legal-style PDF to test the full pipeline.

## Testing without the full UI

Each module can be run standalone to test just that piece:
```bash
cd app
python pdf_extractor.py ../sample_docs/sample_rental_agreement.pdf
python chunker.py ../sample_docs/sample_rental_agreement.pdf
python clause_classifier.py ../sample_docs/sample_rental_agreement.pdf
python risk_detector.py ../sample_docs/sample_rental_agreement.pdf
python vector_store.py ../sample_docs/sample_rental_agreement.pdf
python summarizer.py ../sample_docs/sample_rental_agreement.pdf
python qa_chatbot.py ../sample_docs/sample_rental_agreement.pdf   # interactive chat
```

## Troubleshooting

- **`OSError: [E050] Can't find model 'en_core_web_sm'`** → run step 4 above
- **Very slow first run** → expected, models are downloading; subsequent runs are fast
- **`ModuleNotFoundError`** → venv not activated, or `pip install -r requirements.txt` didn't complete
- **ChromaDB "collection already exists" weirdness** → delete `data/chroma_store/` folder and re-run
- **Out of memory / very slow on CPU** → BART summarization is the heaviest model; if it's too slow on your machine, you can swap `facebook/bart-large-cnn` for a smaller model like `sshleifer/distilbart-cnn-12-6` in `summarizer.py`
- **Port already in use (8000 or 8501)** → close other running instances, or change the port: `uvicorn main:app --reload --port 8001` (and update `API_URL` in `streamlit_app.py` to match)

## Resume-ready description

> Built a full-stack NLP platform (Python, FastAPI, Streamlit) that
> extracts, summarizes, and analyzes legal contracts using transformer
> models. Engineered a semantic search pipeline (PyMuPDF, Sentence
> Transformers, ChromaDB) and a RAG chatbot answering document-grounded
> questions via a Hugging Face extractive QA model. Implemented clause
> classification and rule-based risk detection to flag key contract
> terms (payment, liability, termination, confidentiality) in plain
> language.

## What to actually learn from this (since you'll own this code going forward)

- **Week 1 concepts:** why chunking matters, what embeddings represent geometrically, how vector similarity search works
- **Week 2 concepts:** the difference between extractive QA and generative LLMs, why RAG grounds answers in real source text
- **Week 3 concepts:** why rule-based NLP is sometimes the right choice over ML, trade-offs of keyword matching vs. trained classifiers
- **Week 4 concepts:** REST API design, why frontend/backend are separated, how Streamlit session state works across reruns

If an interviewer asks "why did you choose X model/approach," the comments
in each file explain the actual reasoning — read them, don't just run the code.
