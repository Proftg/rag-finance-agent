import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import rag_tool, sql_tool

load_dotenv()

PROMPT = (
    "You are a financial data analyst assistant. "
    "Use rag_tool to search reports and methodology documents. "
    "Use sql_tool to query the risk-scoring database with real client data. "
    "Answer in the same language as the question. Cite sources when using rag_tool."
)


def build_agent():
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
    return create_react_agent(llm, [rag_tool, sql_tool], prompt=PROMPT)
