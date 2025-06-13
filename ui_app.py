# ui_app.py

import streamlit as st
import json
from script_utils.rag_engine import RAGSearchEngine

@st.cache_resource
def load_engine():
    with open("output/parsed_script.json") as f:
        scenes = json.load(f)
    with open("output/shooting_schedule.json") as f:
        schedule = json.load(f)
    return RAGSearchEngine(scenes, schedule)

st.set_page_config(page_title="Screenplay Q&A", layout="wide")
st.title(" Screenplay Scheduler Q&A (Powered by Mistral + RAG)")
st.text("Whatever the query, SharpShooter is here for you.")

rag = load_engine()

query = st.text_input("Ask a question about the script or shooting schedule:", placeholder="e.g. When is Vedant scheduled?")

if query:
    with st.spinner("Thinking..."):
        answer = rag.query(query)
        st.markdown("### Answer:")
        st.write(answer)
