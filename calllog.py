import json
import time
from config import ROOT

LOG = ROOT / "outputs" / "calls.jsonl"


def ask(agent, question):
    """Run the agent and append one JSON line: question, tools called, seconds, tokens."""
    start = time.time()
    res = agent.invoke({"messages": [("human", question)]})
    msgs = res["messages"]
    record = {
        "question": question,
        "tools": [m.name for m in msgs if m.type == "tool"],
        "seconds": round(time.time() - start, 2),
        "tokens": sum((getattr(m, "usage_metadata", None) or {}).get("total_tokens", 0) for m in msgs),
    }
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return res
