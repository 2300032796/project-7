import streamlit as st
from rag import build_vectorstore, ask_question
from guardrails import (
    check_prompt_injection,
    detect_sensitive_data,
    medical_guard,
    hallucination_guard,
    audit_log,
    show_audit_logs,
    calculate_risk
)
from auth import login, logout, show_user

st.set_page_config(
    page_title="Healthcare RAG Assistant",
    page_icon="🏥",
    layout="wide"
)

# ---------------- LOGIN ----------------

login()
show_user()
logout()

# ---------------- TITLE ----------------

st.title("🏥 Healthcare Coding & Discharge Summary Assistant")

st.write(
    "Upload discharge summaries, ICD coding manuals, or healthcare PDFs. "
    "The assistant retrieves relevant evidence before answering."
)

# ---------------- SESSION ----------------

if "indexed" not in st.session_state:
    st.session_state.indexed = False

# ---------------- PDF Upload ----------------

uploaded_file = st.file_uploader(
    "Upload Healthcare PDF",
    type=["pdf"]
)

if uploaded_file:

    if st.button("Index Document"):

        with st.spinner("Reading PDF and building vector database..."):

            build_vectorstore(uploaded_file)

            st.session_state.indexed = True

        st.success("Document indexed successfully!")

st.divider()

# ---------------- QUESTION ----------------

question = st.text_area(
    "Ask a Question",
    placeholder="Example: Suggest ICD code for diabetes with hypertension."
)

if st.button("Generate Answer"):

    if not st.session_state.indexed:

        st.warning("Upload and index a document first.")
        st.stop()

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    # Prompt Injection Check
    if check_prompt_injection(question):

        st.error("⚠ Prompt Injection Detected")
        st.stop()

    # Risk Analysis
    risk_score, risk_level = calculate_risk(question)

    st.metric("Risk Level", risk_level)

    # Medical Guard
    if not medical_guard(question):

        st.error("Medical safety guard triggered.")
        st.stop()

    # Audit Log
    audit_log(
        st.session_state.role,
        question
    )

    with st.spinner("Searching document..."):

        answer, sources = ask_question(question)

    st.subheader("Answer")
    st.success(answer)

    st.subheader("Evidence")

    for source in sources:
        st.info(source)

    # Display Audit Logs
    show_audit_logs()
