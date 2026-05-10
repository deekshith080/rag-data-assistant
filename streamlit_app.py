import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8001"

st.set_page_config(page_title="Data Catalog Assistant", layout="wide")
st.title("Data Catalog Assistant")
st.caption("Ask questions about your data in plain English. Powered by RAG + Llama3.")

with st.sidebar:
    st.markdown("## Sample Questions")
    questions = [
        "Show me all customers and their subscription plans",
        "What is the total revenue per customer?",
        "Which customers have open support tickets?",
        "Show me churned customers",
        "What is the average monthly price per plan?",
        "Which customers are on the Enterprise plan?",
        "Show me all high priority support tickets",
        "What is the total revenue by industry?",
    ]
    for q in questions:
        if st.button(q, use_container_width=True):
            st.session_state["selected"] = q
    st.markdown("---")
    st.markdown("## Tables")
    st.markdown("- customers")
    st.markdown("- subscriptions")
    st.markdown("- revenue")
    st.markdown("- events")
    st.markdown("- support_tickets")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "selected" not in st.session_state:
    st.session_state["selected"] = ""

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "df" in msg:
            st.dataframe(msg["df"], use_container_width=True)
            with st.expander("View SQL"):
                st.code(msg["sql"], language="sql")
            st.caption("Tables used: " + ", ".join(msg["tables"]))

question = st.chat_input("Ask a question about your data...")

if st.session_state["selected"]:
    question = st.session_state["selected"]
    st.session_state["selected"] = ""

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Generating SQL and fetching results..."):
            try:
                r = requests.post(
                    API_URL + "/query",
                    json={"question": question},
                    timeout=60,
                )
                result = r.json()
                if result.get("success"):
                    msg = "Found " + str(result["row_count"]) + " results."
                    st.markdown(msg)
                    df = pd.DataFrame(result["rows"])
                    st.dataframe(df, use_container_width=True)
                    with st.expander("View SQL"):
                        st.code(result["sql"], language="sql")
                    st.caption("Tables used: " + ", ".join(result["tables_used"]))
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": msg,
                        "df": df,
                        "sql": result["sql"],
                        "tables": result["tables_used"],
                    })
                else:
                    err = "Query failed: " + str(result.get("error", "Unknown error"))
                    st.error(err)
                    st.session_state["messages"].append({"role": "assistant", "content": err})
            except Exception as e:
                err = "API error: " + str(e)
                st.error(err)
                st.session_state["messages"].append({"role": "assistant", "content": err})