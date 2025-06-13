# run_pipeline.py

import json
import os

from script_utils.call_sheet_generator import generate_call_sheets
from script_utils.pdf_extractor import extract_text_from_pdf
from script_utils.parser import parse_screenplay
from script_utils.scheduler import generate_schedule

# 1. Extract text from screenplay PDF
pdf_path = "data/LM.pdf"  # Make sure LM.pdf is inside the /data/ folder
script_text = extract_text_from_pdf(pdf_path)

# 2. Parse scenes from the script text
scenes = parse_screenplay(script_text)

# 3. Save parsed scenes
with open("output/parsed_script.json", "w", encoding="utf-8") as f:
    json.dump(scenes, f, indent=2)

# 4. Generate shooting schedule
schedule = generate_schedule(scenes)

# 5. Save schedule
with open("output/shooting_schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule, f, indent=2)

# 6. Generate call sheets per day
call_sheets = generate_call_sheets(schedule)

# Ensure call_sheets output directory exists
os.makedirs("output/call_sheets", exist_ok=True)

# 7. Save each day's call sheet to its own file
for day, data in call_sheets.items():
    with open(f"output/call_sheets/day_{day}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


print("Parsed scenes saved to output/parsed_script.json")
print("Shooting schedule saved to output/shooting_schedule.json")
print("Call sheets saved to output/call_sheets/")