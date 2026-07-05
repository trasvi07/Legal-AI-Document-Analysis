"""
streamlit_app.py
-----------------
Simple Streamlit UI for the Legal AI platform. Talks to the FastAPI
backend (main.py) over HTTP — this is the standard pattern of separating
the API layer from the UI layer, even in a student project.

Run the backend first:
    uvicorn main:app --reload

Then run this in a separate terminal:
    streamlit run streamlit_app.py
"""

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Legal AI", layout="wide")
st.title("📄 Legal AI — Document Analysis Assistant")
st.caption("Upload a contract or legal document to get a plain-language summary, clause breakdown, risk flags, and ask questions about it.")

# Session state holds the current doc_id across reruns (Streamlit reruns
# the whole script on every interaction, so we need this to persist state)
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Upload section ---
uploaded_file = st.file_uploader("Upload a legal document (PDF)", type=["pdf"])

if uploaded_file is not None and st.button("Process Document"):
    with st.spinner("Extracting text, chunking, and embedding — this may take a moment..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{API_URL}/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        st.session_state.doc_id = data["doc_id"]
        st.session_state.chat_history = []  # reset chat for new document
        st.success(f"Processed '{data['filename']}' — {data['num_pages']} pages, {data['num_chunks']} chunks.")
    else:
        st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")

# --- Analysis tabs (only shown once a document is processed) ---
if st.session_state.doc_id:
    doc_id = st.session_state.doc_id
    tab_summary, tab_clauses, tab_risks, tab_chat = st.tabs(
        ["📝 Summary", "📋 Clauses", "⚠️ Risk Flags", "💬 Ask Questions"]
    )

    with tab_summary:
        if st.button("Generate Summary"):
            with st.spinner("Summarizing..."):
                res = requests.get(f"{API_URL}/summary/{doc_id}")
            if res.status_code == 200:
                st.write(res.json()["summary"])
            else:
                st.error("Could not generate summary.")

    with tab_clauses:
        if st.button("Classify Clauses"):
            with st.spinner("Classifying..."):
                res = requests.get(f"{API_URL}/clauses/{doc_id}")
            if res.status_code == 200:
                clauses = res.json()["clauses"]
                for clause_type, sentences in clauses.items():
                    if clause_type == "unclassified" or not sentences:
                        continue
                    with st.expander(f"{clause_type.title()} ({len(sentences)})"):
                        for s in sentences:
                            st.write(f"- {s}")
            else:
                st.error("Could not classify clauses.")

    with tab_risks:
        if st.button("Detect Risky Terms"):
            with st.spinner("Scanning for risky clauses..."):
                res = requests.get(f"{API_URL}/risks/{doc_id}")
            if res.status_code == 200:
                risks = res.json()["risks"]
                if not risks:
                    st.info("No risky patterns detected in this document.")
                else:
                    for r in risks:
                        st.warning(f"**\"{r['matched_phrase']}\"** — {r['risk']}")
                        st.caption(f"Suggestion: {r['suggestion']}")
            else:
                st.error("Could not run risk detection.")

    with tab_chat:
        st.write("Ask a question about the uploaded document:")

        for role, message in st.session_state.chat_history:
            with st.chat_message(role):
                st.write(message)

        question = st.chat_input("Type your question...")
        if question:
            st.session_state.chat_history.append(("user", question))
            with st.spinner("Thinking..."):
                res = requests.post(f"{API_URL}/chat", json={"doc_id": doc_id, "question": question})

            if res.status_code == 200:
                data = res.json()
                answer_text = f"{data['answer']}  \n\n*(confidence: {data['confidence']}, source page: {data['source_page']})*"
            else:
                answer_text = "Sorry, I couldn't process that question."

            st.session_state.chat_history.append(("assistant", answer_text))
            st.rerun()
else:
    st.info("Upload a document above to get started.")
