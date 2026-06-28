from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "data" / "docs"
WIKI_DIR = ROOT / "data" / "wiki"
CHROMA_DIR = str(ROOT / "outputs" / "chroma")
WIKI_CHROMA_DIR = str(ROOT / "outputs" / "chroma_wiki")
DB_PATH = ROOT / "data" / "risk.sqlite"
EMBED_MODEL = "all-MiniLM-L6-v2"
