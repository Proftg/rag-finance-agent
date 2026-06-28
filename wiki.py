"""Governed LLM wiki: stage agent answers as OKF fiches in a separate Chroma
collection. Generated knowledge is never read by the agent until a human promotes
it into the trusted corpus (data/docs). That promotion is the governance gate."""
import re
import sys
import hashlib
from datetime import datetime, timezone

import yaml
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from config import DOCS_DIR, WIKI_DIR, WIKI_CHROMA_DIR, EMBED_MODEL
from ingest import parse_okf

_emb = None
_wvs = None


def _embeddings():
    global _emb
    if _emb is None:
        _emb = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)
    return _emb


def _wiki_vs():
    global _wvs
    if _wvs is None:
        _wvs = Chroma(persist_directory=WIKI_CHROMA_DIR, embedding_function=_embeddings(),
                      collection_metadata={"hnsw:space": "cosine"})
    return _wvs


def _slug(text):
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]
    return f"{base or 'fiche'}-{hashlib.sha1(text.encode()).hexdigest()[:6]}"


def _fiche_md(question, answer):
    meta = {
        "type": "Generated",
        "title": question[:80],
        "description": "Auto-generated answer pending human review.",
        "tags": ["generated"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provenance": "llm",
        "status": "unreviewed",
        "source_question": question,
    }
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
    return f"---\n{front}---\n\n# {question}\n\n{answer}\n"


def maybe_save(question, answer, threshold=0.9):
    """Stage an answer as an OKF fiche unless a near-duplicate question is already
    staged. Returns the slug if written, None on a semantic cache hit."""
    vs = _wiki_vs()
    hits = vs.similarity_search_with_relevance_scores(question, k=1)
    if hits and hits[0][1] >= threshold:
        return None  # ponytail: cosine 0.9 dedup heuristic, tune if it over/under-merges
    slug = _slug(question)
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    (WIKI_DIR / f"{slug}.md").write_text(_fiche_md(question, answer), encoding="utf-8")
    # index the question only: this collection exists for dedup, not for retrieval
    vs.add_texts([question], metadatas=[{"slug": slug, "title": question[:80]}], ids=[slug])
    return slug


def list_fiches():
    if not WIKI_DIR.exists():
        return []
    out = []
    for p in sorted(WIKI_DIR.glob("*.md")):
        _, meta = parse_okf(p.read_text(encoding="utf-8"), p.name)
        out.append((p.stem, meta.get("title", p.stem)))
    return out


def promote(slug):
    """Move a fiche into the trusted corpus and index it live so the agent can use it."""
    src = WIKI_DIR / f"{slug}.md"
    text = src.read_text(encoding="utf-8").replace("status: unreviewed", "status: reviewed", 1)
    dest = DOCS_DIR / f"{slug}.md"
    dest.write_text(text, encoding="utf-8")
    src.unlink()
    _wiki_vs().delete(ids=[slug])
    from tools import get_vs  # lazy import breaks the tools<->wiki cycle
    body, meta = parse_okf(text, dest.name)
    get_vs().add_texts([body], metadatas=[meta], ids=[slug])
    return dest


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "promote":
        print("Promoted to", promote(sys.argv[2]))
    else:
        for slug, title in list_fiches():
            print(f"{slug}\t{title}")
