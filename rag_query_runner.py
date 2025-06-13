# rag_query_runner.py

import json
from script_utils.rag_engine import RAGSearchEngine

# Load parsed scenes and shooting schedule
with open("output/parsed_script.json") as f:
    scenes = json.load(f)

with open("output/shooting_schedule.json") as f:
    schedule = json.load(f)

# Start RAG engine with both datasets
rag = RAGSearchEngine(scenes, schedule)

# Interactive Q&A loop
while True:
    query = input("\nAsk a question about the script/schedule (or 'q' to quit): ")
    if query.lower() == 'q':
        break
    answer = rag.query(query)
    print("\n Answer:\n", answer)
