from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".docx"]

def load_documents(directory: str) -> List[Document]:
    docs = []
    path = Path(directory)
    for file_path in path.rglob("*"):
        ext = file_path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            doc = Document(
                page_content=text,
                metadata={
                    "source_file": file_path.name,
                    "file_type": ext,
                    "page": 1,
                }
            )
            docs.append(doc)
            logger.info(f"Loaded: {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to load {file_path.name}: {e}")
    return docs

def chunk_documents(documents: List[Document], chunk_size=512, chunk_overlap=64) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks

def ingest_directory(directory: str) -> List[Document]:
    docs = load_documents(directory)
    if not docs:
        raise ValueError(f"No supported documents found in {directory}")
    return chunk_documents(docs)