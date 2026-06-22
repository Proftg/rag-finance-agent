from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from config import DOCS_DIR, CHROMA_DIR, EMBED_MODEL


def run():
    docs = []
    for path in DOCS_DIR.iterdir():
        if path.suffix in (".md", ".txt"):
            docs.extend(TextLoader(str(path), encoding="utf-8").load())
        elif path.suffix == ".pdf":
            docs.extend(PyPDFLoader(str(path)).load())

    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
    Chroma.from_documents(chunks, SentenceTransformerEmbeddings(model_name=EMBED_MODEL), persist_directory=CHROMA_DIR)
    print(f"Indexed {len(chunks)} chunks from {len(docs)} documents")


if __name__ == "__main__":
    run()
