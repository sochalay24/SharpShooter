import re
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from script_utils.ner_tagger import extract_known_characters_from_actions

# Screen direction terms that should never be treated as characters
blacklist = {
    "CUT TO", "FADE IN", "FADE OUT", "BEAT.", "THE END", "SHARP CUT TO",
    "DISSOLVE TO", "MATCH CUT", "EASE IN", "EASE OUT", "BLACKOUT", "BACK TO SCENE"
}

def extract_location_and_time(heading):
    # Extracts location and time from heading
    match = re.search(r'(INT\.|EXT\.|INT/EXT\.?)\s+(.+?)(?:\s*[-\.]\s*(DAY|NIGHT|EVENING|MORNING))?$', heading.strip(), re.IGNORECASE)
    if match:
        location = match.group(2).strip().upper()
        time_of_day = (match.group(3) or "UNKNOWN").upper()
        return location, time_of_day
    return "UNKNOWN", "UNKNOWN"

def parse_screenplay(script_text):
    scenes = []
    lines = script_text.splitlines()
    scene = None
    scene_count = 0

    scene_heading_pattern = re.compile(r'^\s*(\d+[A-Z]*\.)?\s*(INT\.|EXT\.|INT/EXT\.|I/E\.)\s+.+', re.IGNORECASE)
    character_pattern = re.compile(r'^[A-Z][A-Z0-9\s\.]{1,}$')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Detect scene headings
        if scene_heading_pattern.match(stripped):
            if scene:
                scenes.append(scene)
            scene_count += 1
            location, time_of_day = extract_location_and_time(stripped)
            scene = {
                "scene_number": scene_count,
                "heading": stripped,
                "location": location,
                "time_of_day": time_of_day,
                "characters": [],
                "actions": []  # Add temporarily to capture action text
            }
            continue

        # Detect character names
        if scene and character_pattern.match(stripped):
            word_count = len(stripped.split())
            upper_text = stripped.upper()

            if 1 <= word_count <= 2 and upper_text not in blacklist:
                character = upper_text.strip()
                if character not in scene["characters"]:
                    scene["characters"].append(character)
                continue

        # Otherwise treat as action line
        if scene:
            scene["actions"].append(stripped)

    if scene:
        scenes.append(scene)

    # 🔍 STEP 1: Gather known characters
    all_known_characters = set()
    for sc in scenes:
        all_known_characters.update(sc["characters"])

    # 🔍 STEP 2: Scan actions for silent characters
    for sc in scenes:
        if "actions" in sc:
            silent_characters = extract_known_characters_from_actions(sc["actions"], all_known_characters)
            for char in silent_characters:
                if char not in sc["characters"]:
                    sc["characters"].append(char)

    # Optional: Remove actions before returning
    for sc in scenes:
        sc.pop("actions", None)

    return scenes

if __name__ == "__main__":
    with open("output/raw_script.txt", "r", encoding="utf-8") as f:
        script_text = f.read()

    scenes = parse_screenplay(script_text)

    with open("output/parsed_script.json", "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=2, ensure_ascii=False)

    print(f" Parsed {len(scenes)} scenes. Output saved to output/parsed_script.json")
