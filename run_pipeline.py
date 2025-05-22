# run_pipeline.py
from script_utils.pdf_extractor import extract_text_from_pdf
from script_utils.parser import parse_screenplay
from script_utils.ner_tagger import extract_entities
from script_utils.scheduler import create_schedule
from script_utils.call_sheet_generator import generate_call_sheets
import json

pdf_path = "LM.pdf"
text = extract_text_from_pdf(pdf_path)
scenes = parse_screenplay(text)

# Enrich with props/equipment
for scene in scenes:
    scene["props"] = extract_entities(scene["description"])
    scene["equipment"] = ["Camera", "Lighting Kit"]  # Hardcoded or inferred later

with open("output/parsed_script.json", "w") as f:
    json.dump(scenes, f, indent=2)

schedule = create_schedule(scenes)
with open("output/shooting_schedule.json", "w") as f:
    json.dump(schedule, f, indent=2)

call_sheets = generate_call_sheets(schedule)
for day, data in call_sheets.items():
    with open(f"output/call_sheets/day_{day}.json", "w") as f:
        json.dump(data, f, indent=2)
