import sqlite3
import pandas as pd
from langchain.tools import tool
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from config import CHROMA_DIR, DB_PATH, EMBED_MODEL

_vs = None


def get_vs():
    global _vs
    if _vs is None:
        _vs = Chroma(persist_directory=CHROMA_DIR, embedding_function=SentenceTransformerEmbeddings(model_name=EMBED_MODEL))
    return _vs


@tool
def rag_tool(query: str) -> str:
    """Search financial documents (reports, methodology, results) to answer questions
    about risk scoring, fraud detection, data quality, or pipeline architecture."""
    results = get_vs().similarity_search(query, k=4)
    if not results:
        return "No relevant document found."
    return "\n\n---\n\n".join(f"[{_cite(r.metadata)}]\n{r.page_content}" for r in results)


def _cite(meta: dict) -> str:
    """Build an OKF-aware citation: title (type) [tags] falling back to source."""
    label = meta.get("title") or meta.get("source", "doc")
    if meta.get("type"):
        label += f" ({meta['type']})"
    if meta.get("tags"):
        label += f" [tags: {meta['tags']}]"
    return label


@tool
def sql_tool(query: str) -> str:
    """Run a read-only SQL query on the scored_clients table (columns: ID, risk_score,
    anomaly, default_flag, limit_bal_eur, education_label, marriage_label, age_band,
    risk_decile). Use for statistics, counts, averages, or specific client lookups."""
    if not DB_PATH.exists():
        return "Database not found."
    if any(w in query.lower() for w in ["drop", "delete", "insert", "update", "alter", "create"]):
        return "Only SELECT queries are allowed."
    try:
        with sqlite3.connect(DB_PATH) as con:
            df = pd.read_sql(query, con)
        return "No results." if df.empty else df.to_string(index=False, max_rows=20)
    except Exception as e:
        return f"SQL error: {e}"
