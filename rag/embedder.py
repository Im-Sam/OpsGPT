from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_PATH = "data/vectorstore"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def build_vectorstore(chunks: List[Document]) -> FAISS:
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    logger.info(f"Vectorstore saved — {len(chunks)} vectors")
    return vectorstore

def load_vectorstore() -> FAISS:
    if not Path(f"{VECTORSTORE_PATH}/index.faiss").exists():
        raise FileNotFoundError("No vectorstore found. Ingest documents first.")
    embeddings = get_embeddings()
    return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)

def add_documents(chunks: List[Document], vectorstore=None) -> FAISS:
    if vectorstore is None:
        try:
            vectorstore = load_vectorstore()
            vectorstore.add_documents(chunks)
        except FileNotFoundError:
            vectorstore = build_vectorstore(chunks)
    else:
        vectorstore.add_documents(chunks)
    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore