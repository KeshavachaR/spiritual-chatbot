# app/ingest.py

import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DATA_PATH = Path(__file__).parent / "data" / "bible.txt"
PERSIST_DIR = str(Path(__file__).parent / "chroma_bible")

def load_corpus():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", "? ", "! ", " "],
    )
    return splitter.create_documents([text])

def build_index():
    text = load_corpus()
    docs = chunk_text(text)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = Chroma(collection_name="bible", embedding_function=embeddings, persist_directory=PERSIST_DIR)
    vs.add_documents(docs)
    vs.persist()
    print(f"Indexed {len(docs)} chunks into {PERSIST_DIR}")

if __name__ == "__main__":
    os.makedirs(Path(PERSIST_DIR), exist_ok=True)
    build_index()