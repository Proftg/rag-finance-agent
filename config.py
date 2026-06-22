from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "data" / "docs"
CHROMA_DIR = str(ROOT / "outputs" / "chroma")
DB_PATH = ROOT.parent / "spf-risk-scoring" / "outputs" / "risk.sqlite"
EMBED_MODEL = "all-MiniLM-L6-v2"
