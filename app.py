import streamlit as st
import tempfile
from transformers import pipeline
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline

st.set_page_config(page_title="Healthcare RAG Assistant", layout="wide")
st.title("🏥 Healthcare Coding & Discharge Summary Assistant")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

def load_pdf(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        path = tmp.name
    return PyPDFLoader(path).load()

def split_docs(docs):
    return RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100).split_documents(docs)

@st.cache_resource
def embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def load_llm():
    return HuggingFacePipeline(pipeline=pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=256))

if uploaded:
    docs = load_pdf(uploaded)
    chunks = split_docs(docs)
    db = Chroma.from_documents(chunks, embedding_model(), persist_directory="chroma_db")
    qa = RetrievalQA.from_chain_type(llm=load_llm(), retriever=db.as_retriever(search_kwargs={"k":3}), return_source_documents=True)

    question = st.text_area("Ask a medical question")
    if st.button("Generate Answer") and question:
        result = qa({"query": question})
        st.subheader("Answer")
        st.write(result["result"])
        st.subheader("Evidence")
        for i, d in enumerate(result["source_documents"],1):
            st.markdown(f"### Chunk {i}")
            st.write(d.page_content)
            st.caption(d.metadata)
else:
    st.info("Upload a PDF to begin.")
