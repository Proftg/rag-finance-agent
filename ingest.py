import shutil

import yaml
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from config import DOCS_DIR, CHROMA_DIR, EMBED_MODEL


def parse_okf(text, source):
    """Split OKF front-matter from the body. Returns (body, metadata).
    Chroma metadata must be scalars, so lists are joined and other types stringified."""
    meta = {"source": source}
    if text.startswith("---"):
        _, front_matter, text = text.split("---", 2)
        for key, value in (yaml.safe_load(front_matter) or {}).items():
            if isinstance(value, list):
                meta[key] = ", ".join(str(v) for v in value)
            elif isinstance(value, (str, int, float, bool)):
                meta[key] = value
            else:
                meta[key] = str(value)
    return text.strip(), meta


def load_okf(path):
    body, meta = parse_okf(path.read_text(encoding="utf-8"), path.name)
    return Document(page_content=body, metadata=meta)


def run():
    docs = []
    for path in DOCS_DIR.iterdir():
        if path.suffix in (".md", ".txt"):
            docs.append(load_okf(path))
        elif path.suffix == ".pdf":
            docs.extend(PyPDFLoader(str(path)).load())

    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)  # idempotent rebuild, no stale/duplicate chunks
    Chroma.from_documents(chunks, SentenceTransformerEmbeddings(model_name=EMBED_MODEL), persist_directory=CHROMA_DIR)
    print(f"Indexed {len(chunks)} chunks from {len(docs)} documents")


if __name__ == "__main__":
    run()
