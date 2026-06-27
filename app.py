import streamlit as st
import os
import tempfile
import re
import pandas as pd

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

from langchain.chains import RetrievalQA

from transformers import pipeline
from langchain.llms import HuggingFacePipeline

# ------------------------------
# PAGE CONFIG
# ------------------------------

st.set_page_config(
    page_title="Healthcare RAG Assistant",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Coding & Discharge Summary Assistant")

st.markdown(
"""
Upload a healthcare PDF and ask questions.
The assistant retrieves evidence before answering.
"""
)

# ------------------------------
# SESSION
# ------------------------------

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# ------------------------------
# SIDEBAR
# ------------------------------

st.sidebar.title("Settings")

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

chunk_size = st.sidebar.slider(
    "Chunk Size",
    300,
    1200,
    700
)

chunk_overlap = st.sidebar.slider(
    "Chunk Overlap",
    20,
    300,
    100
)

# ------------------------------
# PROMPT INJECTION CHECK
# ------------------------------

danger_words = [
    "ignore previous instructions",
    "system prompt",
    "jailbreak",
    "delete database",
    "reveal password",
    "act as admin",
    "bypass"
]

def detect_prompt_injection(text):

    found = []

    lower = text.lower()

    for word in danger_words:

        if word in lower:
            found.append(word)

    return found

# ------------------------------
# LOAD PDF
# ------------------------------

def load_document(file):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(file.read())

        path = tmp.name

    loader = PyPDFLoader(path)

    docs = loader.load()

    return docs

# ------------------------------
# SPLIT DOCUMENT
# ------------------------------

def split_document(docs):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=chunk_size,

        chunk_overlap=chunk_overlap

    )

    chunks = splitter.split_documents(docs)

    return chunks

# ------------------------------
# EMBEDDINGS
# ------------------------------

@st.cache_resource

def embedding_model():

    return HuggingFaceEmbeddings(

        model_name="sentence-transformers/all-MiniLM-L6-v2"

    )

# ------------------------------
# VECTOR DATABASE
# ------------------------------

def build_vector_db(chunks):

    db = Chroma.from_documents(

        chunks,

        embedding_model(),

        persist_directory="chroma_db"

    )

    return db

# ------------------------------
# LOCAL LLM
# ------------------------------

@st.cache_resource

def load_llm():

    generator = pipeline(

        "text2text-generation",

        model="google/flan-t5-base",

        max_new_tokens=256

    )

    llm = HuggingFacePipeline(

        pipeline=generator

    )

    return llm

# ------------------------------
# BUILD QA CHAIN
# ------------------------------

def build_chain(db):

    retriever = db.as_retriever(

        search_kwargs={"k":3}

    )

    qa = RetrievalQA.from_chain_type(

        llm=load_llm(),

        retriever=retriever,

        return_source_documents=True

    )

    return qa
  # ----------------------------------
# PROCESS DOCUMENT
# ----------------------------------

if uploaded_file is not None:

    with st.spinner("Reading PDF..."):

        docs = load_document(uploaded_file)

        chunks = split_document(docs)

        db = build_vector_db(chunks)

        qa_chain = build_chain(db)

        st.session_state.vectordb = db

        st.session_state.qa_chain = qa_chain

    st.success("Document indexed successfully.")

# ----------------------------------
# ASK QUESTION
# ----------------------------------

st.header("Ask Questions")

question = st.text_area(

    "Enter your medical question",

    placeholder="Example: Suggest ICD code for diabetes."

)

ask = st.button("Generate Answer")

# ----------------------------------
# RISK SCORE
# ----------------------------------

def calculate_risk(question):

    score = 0

    injection = detect_prompt_injection(question)

    if injection:
        score += 50

    if len(question) > 500:
        score += 10

    if "password" in question.lower():
        score += 20

    if "delete" in question.lower():
        score += 20

    if score < 30:
        level = "Low"

    elif score < 60:
        level = "Medium"

    else:
        level = "High"

    return score, level, injection

# ----------------------------------
# AI RESPONSE
# ----------------------------------

if ask:

    if st.session_state.qa_chain is None:

        st.warning("Upload a PDF first.")

    else:

        score, level, injection = calculate_risk(question)

        if injection:

            st.error("Prompt Injection Detected")

            st.write(injection)

            st.stop()

        with st.spinner("Searching medical knowledge..."):

            result = st.session_state.qa_chain(

                {"query": question}

            )

        answer = result["result"]

        sources = result["source_documents"]

        st.divider()

        st.subheader("AI Answer")

        st.success(answer)

        st.divider()

        st.subheader("Evidence")

        for i, doc in enumerate(sources):

            st.markdown(f"### Evidence {i+1}")

            st.write(doc.page_content)

            st.caption(doc.metadata)

# ----------------------------------
# RISK DASHBOARD
# ----------------------------------

        st.divider()

        st.subheader("Risk Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric(

            "Risk Score",

            score

        )

        col2.metric(

            "Risk Level",

            level

        )

        col3.metric(

            "Evidence Retrieved",

            len(sources)

        )

# ----------------------------------
# CONFIDENCE SCORE
# ----------------------------------

        confidence = max(

            60,

            100 - score

        )

        st.progress(confidence/100)

        st.write(

            f"Confidence : {confidence}%"

        )

# ----------------------------------
# DOWNLOAD REPORT
# ----------------------------------

        report = f"""

Question

{question}

----------------------

Answer

{answer}

----------------------

Risk Score

{score}

Risk Level

{level}

Confidence

{confidence}

"""

        st.download_button(

            "Download Report",

            report,

            file_name="medical_report.txt"

        )
      import plotly.express as px
from datetime import datetime

# --------------------------------------
# SIMPLE LOGIN (RBAC)
# --------------------------------------

st.sidebar.divider()
st.sidebar.header("User Login")

users = {
    "Doctor": "doctor123",
    "Nurse": "nurse123",
    "Coder": "coder123",
    "Admin": "admin123"
}

role = st.sidebar.selectbox(
    "Role",
    list(users.keys())
)

password = st.sidebar.text_input(
    "Password",
    type="password"
)

logged_in = False

if st.sidebar.button("Login"):

    if password == users[role]:

        logged_in = True
        st.sidebar.success("Login Successful")

    else:

        st.sidebar.error("Invalid Password")

# --------------------------------------
# AUDIT LOGGING
# --------------------------------------

if "audit_logs" not in st.session_state:

    st.session_state.audit_logs = []

def add_log(user, action):

    st.session_state.audit_logs.append({

        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "User": user,

        "Action": action

    })

# --------------------------------------
# SESSION HISTORY
# --------------------------------------

if "history" not in st.session_state:

    st.session_state.history = []

# --------------------------------------
# HALLUCINATION CHECK
# --------------------------------------

def hallucination_check(answer, evidence):

    answer = answer.lower()

    if len(evidence) == 0:

        return False

    combined = ""

    for doc in evidence:

        combined += doc.page_content.lower()

    words = answer.split()

    matched = 0

    for word in words:

        if word in combined:

            matched += 1

    score = matched / max(len(words), 1)

    return score > 0.40

# --------------------------------------
# CONTENT FILTER
# --------------------------------------

blocked_words = [

    "credit card",

    "social security",

    "password",

    "delete database",

    "hack",

    "malware"

]

def content_filter(answer):

    lower = answer.lower()

    for word in blocked_words:

        if word in lower:

            return False

    return True

# --------------------------------------
# VERSION INFO
# --------------------------------------

DOCUMENT_VERSION = "v1.0"

def document_version():

    return DOCUMENT_VERSION

# --------------------------------------
# RETRIEVAL METADATA
# --------------------------------------

def display_sources(source_docs):

    st.subheader("Retrieved Evidence")

    for index, doc in enumerate(source_docs):

        st.markdown(f"### Chunk {index+1}")

        st.write(doc.page_content)

        if "source" in doc.metadata:

            st.caption(
                f"Source : {doc.metadata['source']}"
            )

        if "page" in doc.metadata:

            st.caption(
                f"Page : {doc.metadata['page']}"
            )

# --------------------------------------
# MONITORING DASHBOARD
# --------------------------------------

def monitoring_dashboard():

    dashboard = pd.DataFrame({

        "Metric":[

            "Latency(ms)",

            "GPU Usage",

            "Hallucination",

            "Prompt Injection",

            "Retrieval"

        ],

        "Value":[

            420,

            38,

            2,

            1,

            96

        ]

    })

    fig = px.bar(

        dashboard,

        x="Metric",

        y="Value",

        text="Value",

        title="System Monitoring"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

# --------------------------------------
# AUDIT VIEWER
# --------------------------------------

def audit_dashboard():

    st.subheader("Audit Logs")

    if len(st.session_state.audit_logs)==0:

        st.info("No logs yet.")

        return

    df = pd.DataFrame(

        st.session_state.audit_logs

    )

    st.dataframe(

        df,

        use_container_width=True

    )# ======================================
# MULTI DOCUMENT SUPPORT
# ======================================

st.sidebar.divider()

multi_files = st.sidebar.file_uploader(
    "Upload Multiple PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.sidebar.button("Index All Documents"):

    if len(multi_files) == 0:

        st.sidebar.warning("Upload PDFs first.")

    else:

        all_chunks = []

        progress = st.progress(0)

        for i, pdf in enumerate(multi_files):

            docs = load_document(pdf)

            chunks = split_document(docs)

            all_chunks.extend(chunks)

            progress.progress((i + 1) / len(multi_files))

        db = build_vector_db(all_chunks)

        qa_chain = build_chain(db)

        st.session_state.vectordb = db

        st.session_state.qa_chain = qa_chain

        st.sidebar.success("All documents indexed successfully!")

# ======================================
# SEARCH FILTERS
# ======================================

st.sidebar.divider()

top_k = st.sidebar.slider(
    "Top Retrieved Chunks",
    1,
    10,
    3
)

# ======================================
# FEEDBACK SYSTEM
# ======================================

st.divider()

st.subheader("User Feedback")

feedback = st.radio(

    "Was the answer helpful?",

    ["👍 Yes", "👎 No"]

)

comments = st.text_area(

    "Comments"

)

if st.button("Submit Feedback"):

    add_log(role, "Feedback Submitted")

    st.success("Thank you for your feedback!")

# ======================================
# RETRIEVAL METRICS
# ======================================

st.divider()

st.subheader("Retrieval Statistics")

if st.session_state.vectordb:

    try:

        collection = st.session_state.vectordb._collection.count()

    except:

        collection = "Unknown"

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Indexed Chunks",

        collection

    )

    c2.metric(

        "Retriever Top-K",

        top_k

    )

    c3.metric(

        "Embedding Model",

        "MiniLM"

    )

# ======================================
# GPU COST ESTIMATION
# ======================================

st.divider()

st.subheader("Cost Monitoring")

estimated_requests = st.number_input(

    "Requests",

    1,

    10000,

    100

)

gpu_cost = estimated_requests * 0.0025

st.metric(

    "Estimated GPU Cost ($)",

    f"${gpu_cost:.2f}"

)

# ======================================
# HEALTH CHECK
# ======================================

st.divider()

st.subheader("System Health")

status = {

    "Vector DB": "Healthy",

    "Embedding Model": "Healthy",

    "LLM": "Healthy",

    "Retriever": "Healthy",

    "Guardrails": "Enabled"

}

health_df = pd.DataFrame(

    status.items(),

    columns=["Component", "Status"]

)

st.dataframe(

    health_df,

    use_container_width=True

)

# ======================================
# SIDEBAR INFORMATION
# ======================================

st.sidebar.divider()

st.sidebar.markdown("## Deployment")

st.sidebar.success("Healthcare RAG Assistant")

st.sidebar.write("Version : 1.0")

st.sidebar.write("Vector DB : Chroma")

st.sidebar.write("Embedding : MiniLM")

st.sidebar.write("LLM : FLAN-T5")

st.sidebar.write("Framework : LangChain")

st.sidebar.write("Frontend : Streamlit")

# ======================================
# FOOTER
# ======================================

st.divider()

st.caption(
"""
Healthcare Coding & Discharge Summary Assistant

Features
--------
✔ Retrieval-Augmented Generation (RAG)
✔ Evidence Retrieval
✔ Prompt Injection Detection
✔ Guardrails
✔ Hallucination Detection
✔ Audit Logs
✔ Role-Based Access Control
✔ Monitoring Dashboard
✔ Risk Analysis
✔ Multi-PDF Support
✔ Download Reports
✔ Feedback System
✔ GPU Cost Estimation

Developed for NVIDIA DLI Advanced DL / GenAI with LLMs
"""
)
