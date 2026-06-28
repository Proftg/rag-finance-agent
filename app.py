import streamlit as st
import wiki
from agent import build_agent

st.set_page_config(page_title="Financial RAG Agent", page_icon="🤖", layout="centered")
st.title("Financial RAG Agent")
st.caption("ReAct agent · document search + SQL queries · Groq / Llama 3.3 70B")

if "agent" not in st.session_state:
    with st.spinner("Loading..."):
        st.session_state["agent"] = build_agent()

if "history" not in st.session_state:
    st.session_state["history"] = []

examples = [
    "What is the AUC score for fraud detection?",
    "Quel est le taux de défaut moyen par décile de risque ?",
    "How many clients per education level are flagged as anomalies?",
    "Quelle est la méthodologie de scoring utilisée ?",
]

with st.expander("Example questions"):
    cols = st.columns(2)
    for i, q in enumerate(examples):
        if cols[i % 2].button(q, key=f"ex_{i}", use_container_width=True):
            st.session_state["autosubmit"] = q
            st.rerun()

question = st.text_input("Question", placeholder="Ask in French or English...", label_visibility="collapsed")
send = st.button("Send", use_container_width=True, type="primary")

pending = st.session_state.pop("autosubmit", None) or (question.strip() if send else None)

if pending:
    st.session_state["history"].append({"role": "user", "content": pending})
    with st.spinner("Thinking..."):
        try:
            res = st.session_state["agent"].invoke({"messages": [("human", pending)]})
            answer = res["messages"][-1].content
        except Exception as e:
            answer = f"Error: {e}"
    st.session_state["history"].append({"role": "assistant", "content": answer})
    if not answer.startswith("Error:"):
        wiki.maybe_save(pending, answer)

with st.sidebar:
    st.subheader("Generated wiki")
    st.caption("OKF fiches staged from answers. Promote to add to the trusted corpus.")
    fiches = wiki.list_fiches()
    if not fiches:
        st.caption("None staged yet.")
    for slug, title in fiches:
        if st.button(f"Promote: {title}", key=f"pr_{slug}", use_container_width=True):
            wiki.promote(slug)
            st.rerun()

if st.session_state["history"]:
    st.divider()
    for msg in st.session_state["history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
