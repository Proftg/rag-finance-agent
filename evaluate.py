"""Run the agent on a few questions with known answers and score routing and content."""
import sqlite3
from agent import build_agent
from config import DB_PATH
from trace import ask

with sqlite3.connect(DB_PATH) as con:
    defaults = con.execute("select sum(default_flag) from scored_clients").fetchone()[0]
    avg_limit = int(con.execute("select avg(limit_bal_eur) from scored_clients").fetchone()[0])

# (question, expected tool, text the answer must contain)
CASES = [
    ("What is the AUC score for fraud detection?", "rag_tool", "0.945"),
    ("What is the fraud rate among flagged transactions?", "rag_tool", "10"),
    ("Quelle est la méthodologie de scoring ?", "rag_tool", "Isolation Forest"),
    ("How many clients are in the database?", "sql_tool", "30000"),
    ("Combien de clients sont en défaut de paiement ?", "sql_tool", str(defaults)),
    ("What is the average credit limit in euros, rounded down?", "sql_tool", str(avg_limit)),
    ("How many clients are flagged as anomalies?", "sql_tool", "1500"),
]


def clean(text):
    return text.replace(",", "").replace(" ", "").replace(" ", "").replace("\xa0", "")


def run():
    agent = build_agent()
    ok = 0
    for question, tool, expected in CASES:
        res = ask(agent, question)
        used = {m.name for m in res["messages"] if m.type == "tool"}
        answer = clean(res["messages"][-1].content)
        right = tool in used and clean(expected) in answer
        ok += right
        print(f"{'PASS' if right else 'FAIL'}  {question}  (tools: {sorted(used)}, expected {expected})")
    print(f"\n{ok}/{len(CASES)} correct")


if __name__ == "__main__":
    run()
