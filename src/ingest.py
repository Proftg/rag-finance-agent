from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "data" / "docs"
CHROMA_DIR = str(ROOT / "outputs" / "chroma")


def run():
    docs = []
    for path in DOCS_DIR.iterdir():
        if path.suffix in (".md", ".txt"):
            docs.extend(TextLoader(str(path), encoding="utf-8").load())
        elif path.suffix == ".pdf":
            docs.extend(PyPDFLoader(str(path)).load())

    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    print(f"Indexed {len(chunks)} chunks from {len(docs)} documents")


if __name__ == "__main__":
    run()
