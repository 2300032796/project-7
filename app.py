import os
import tempfile
import streamlit as st

from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.prompts import ChatPromptTemplate

from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain.chains import create_retrieval_chain

CHROMA_PATH = "chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatGroq(
    api_key=st.secrets["GROQ_API_KEY"],
    model="llama3-8b-8192",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
"""
You are a healthcare coding assistant.

Use ONLY the provided context.

If the answer is not available in the context,
reply with

"I don't know."

<context>

{context}

</context>

Question:

{input}
"""
)

def index_pdf(uploaded_file):

    if os.path.exists(CHROMA_PATH):

        import shutil

        shutil.rmtree(CHROMA_PATH)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(uploaded_file.read())

        pdf_path = tmp.name

    loader = PyPDFLoader(pdf_path)

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=700,

        chunk_overlap=100

    )

    chunks = splitter.split_documents(docs)

    Chroma.from_documents(

        documents=chunks,

        embedding=embeddings,

        persist_directory=CHROMA_PATH

    )

def ask_question(question):

    db = Chroma(

        persist_directory=CHROMA_PATH,

        embedding_function=embeddings

    )

    retriever = db.as_retriever(

        search_kwargs={"k":3}

    )

    document_chain = create_stuff_documents_chain(

        llm,

        prompt

    )

    chain = create_retrieval_chain(

        retriever,

        document_chain

    )

    response = chain.invoke({

        "input": question

    })

    answer = response["answer"]

    evidence = []

    for doc in response["context"]:

        page = doc.metadata.get("page",0)

        evidence.append(

            f"Page {page+1}: {doc.page_content[:300]}..."

        )

    return answer,evidence
