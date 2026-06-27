import os
import tempfile
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain_groq import ChatGroq

from langchain.chains import RetrievalQA

# -----------------------------
# Configuration
# -----------------------------

CHROMA_DIR = "chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatGroq(
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model="llama3-8b-8192",
    temperature=0
)

# -----------------------------
# Build Vector Store
# -----------------------------

def build_vectorstore(uploaded_file):

    if os.path.exists(CHROMA_DIR):
        import shutil
        shutil.rmtree(CHROMA_DIR)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )

    return vector_db

# -----------------------------
# Ask Question
# -----------------------------

def ask_question(question):

    vector_db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

    retriever = vector_db.as_retriever(
        search_kwargs={"k": 3}
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    result = qa.invoke({"query": question})

    answer = result["result"]

    evidence = []

    for doc in result["source_documents"]:

        page = doc.metadata.get("page", "Unknown")

        evidence.append(
            f"Page {page + 1}: {doc.page_content[:350]}..."
        )

    return answer, evidence
