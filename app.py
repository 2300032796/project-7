import streamlit as st

from auth import login
from rag import index_pdf, ask_question

st.set_page_config(
    page_title="Healthcare RAG Assistant",
    page_icon="🏥",
    layout="wide"
)

login()

st.title("🏥 Healthcare Coding Assistant")

uploaded = st.file_uploader(
    "Upload Healthcare PDF",
    type=["pdf"]
)

if uploaded:

    if st.button("Index Document"):

        with st.spinner("Indexing PDF..."):

            index_pdf(uploaded)

        st.success("Document Indexed Successfully")

question = st.text_area(
    "Ask a Medical Question"
)

if st.button("Generate Answer"):

    if question.strip() == "":
        st.warning("Enter a question")
        st.stop()

    answer, sources = ask_question(question)

    st.subheader("Answer")

    st.write(answer)

    st.subheader("Evidence")

    for source in sources:

        st.info(source)
