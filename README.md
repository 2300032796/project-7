# 🏥 Healthcare RAG Assistant

A production-style Healthcare Coding & Discharge Summary Assistant built using:

- Streamlit
- LangChain
- Groq Llama 3
- ChromaDB
- HuggingFace Embeddings

## Features

- PDF Upload
- Retrieval-Augmented Generation (RAG)
- Evidence Retrieval
- Prompt Injection Detection
- Role-Based Login
- Risk Score Dashboard
- Audit Logging
- Download Reports
- Healthcare Guardrails

---

## Project Structure

Healthcare-RAG/

├── app.py

├── rag.py

├── auth.py

├── guardrails.py

├── requirements.txt

└── README.md

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run

```bash
streamlit run app.py
```

---

## Streamlit Secrets

Create

.streamlit/secrets.toml

```toml
GROQ_API_KEY="your_groq_api_key"
```

---

## Deployment

1. Push to GitHub
2. Deploy on Streamlit Community Cloud
3. Add GROQ_API_KEY in Streamlit Secrets
4. Deploy

---

## Technologies

- Python
- Streamlit
- LangChain
- ChromaDB
- HuggingFace
- Groq
- Llama 3

---

## Future Improvements

- OCR
- Multi-PDF Search
- Medical Image Analysis
- HIPAA Compliance
- Dashboard Analytics

---

## Author

Healthcare RAG Assistant
NVIDIA DLI Advanced DL / GenAI with LLMs
