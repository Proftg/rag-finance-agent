# Financial RAG Agent

An agentic RAG system that answers questions about financial risk data using two tools:

- **Document search (RAG)**: semantic search over indexed reports and methodology docs (ChromaDB + sentence-transformers)
- **SQL queries**: direct queries on a SQLite database of 30,000 scored clients

The agent (ReAct / LangGraph) decides which tool to use based on the question. Answers in French or English.

Documents are structured with [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog) (Google's Open Knowledge Format), and the agent feeds a **governed wiki**: every answer is staged as a new OKF note, but it only re-enters the trusted corpus after explicit human approval.

![Demo](assets/demo.gif)

## Knowledge governance: OKF + governed wiki

The project is built around the lifecycle of knowledge, not just the model:

```
curated OKF docs ──rag_tool──> agent answers ──stage──> generated OKF note (unreviewed)
       ▲                                                          │
       └──────────────── promote() [human gate] ─────────────────┘
```

- **OKF (how knowledge enters)**: each doc carries a YAML front-matter (`type`, `title`, `tags`, `timestamp`, ...). At ingestion the YAML is parsed, stripped from the embedded text, and pushed as ChromaDB metadata, so citations show `title (type) [tags]` instead of a raw path.
- **RAG (how knowledge is retrieved)**: factual grounding, traceability, citations.
- **Governed wiki (how knowledge grows)**: answers are staged as OKF notes (`status: unreviewed`) in a **separate** ChromaDB collection, deduplicated on write (cosine >= 0.9). The agent never reads generated notes. A note enters the trusted corpus only when a human clicks **Promote** in the sidebar. This human gate makes self-poisoning impossible by construction.

## Stack

Python · LangChain · LangGraph · ChromaDB · Groq (Llama 3.3 70B) · Streamlit · sentence-transformers · OKF

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

## Usage

```bash
# Index documents (run once)
python ingest.py

# Launch the dashboard
streamlit run app.py
```

## Example questions

- *What is the AUC score for fraud detection?* → RAG on reports
- *Quel est le taux de défaut moyen par décile de risque ?* → SQL on scored clients
- *How many anomalies per education level?* → SQL aggregation
- *Quelle est la méthodologie de scoring ?* → RAG on methodology docs

## Data

The SQL tool connects to the `scored_clients` table from the [spf-risk-scoring](https://github.com/Proftg/spf-risk-scoring) project (30k clients, Isolation Forest scoring).
