import sqlite3
from functools import cache

import pandas as pd
from langchain.tools import tool
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from config import CHROMA_DIR, DB_PATH, EMBED_MODEL


@cache
def embeddings():
    return SentenceTransformerEmbeddings(model_name=EMBED_MODEL)


@cache
def get_vs():
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings())


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
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as con:  # read-only: writes fail at the DB level
            df = pd.read_sql(query, con)
        return "No results." if df.empty else df.to_string(index=False, max_rows=20)
    except Exception as e:
        return f"SQL error: {e}"
