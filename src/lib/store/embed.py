from pandas import DataFrame
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import streamlit as st

from config.config import VECTOR_STORE, EMBEDDING, DOCUMENT_DIR
from .load_data import load_data


def embed_df(file: str, parse_dates=None, match={}):
    key = f"embedding_{file}"
    if key in st.session_state:
        print(key)
        return st.session_state[key]

    print('Loading DF')
    df = load_data(file, parse_dates)

    if match:
        df = df[df[match['key']] == match['value']]

    texts = df.apply(lambda row: " ".join(map(str, row.values)), axis=1).tolist()

    print('Embedding DF')
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(texts)
    db = VECTOR_STORE.from_documents(docs, embedding=EMBEDDING)

    st.session_state[key] = db
    return db


def embed_pdf(file: str):
    key = f"embedding_{file}"
    if key in st.session_state:
        return st.session_state[key]

    path = os.path.join(DOCUMENT_DIR, file)
    loader = PyPDFLoader(path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = loader.load_and_split(text_splitter=splitter)
    db = VECTOR_STORE.from_documents(docs, embedding=EMBEDDING)
    
    st.session_state[key] = db
    return db


def embed_text(file: str):
    key = f"embedding_{file}"
    if key in st.session_state:
        return st.session_state[key]

    path = os.path.join(DOCUMENT_DIR, file)
    loader = TextLoader(path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = loader.load_and_split(text_splitter=splitter)
    db = VECTOR_STORE.from_documents(docs, embedding=EMBEDDING)
    return db