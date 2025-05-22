import re
import json

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

    # Matches headings like "1.INT. LOCATION - NIGHT"
    scene_heading_pattern = re.compile(r'^\s*(\d+[A-Z]*\.)?\s*(INT\.|EXT\.|INT/EXT\.|I/E\.)\s+.+', re.IGNORECASE)
    character_pattern = re.compile(r'^[A-Z][A-Z\s\.]{2,}$')  # Allows periods in names


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
            }
            continue


        # Detect characters only if a scene exists
        if scene and character_pattern.match(stripped) and len(stripped.split()) <= 4:
            character = stripped.strip()
            if character not in scene["characters"]:
                scene["characters"].append(character)
            continue



    # Add last scene
    if scene:
        scenes.append(scene)

    return scenes

if __name__ == "__main__":
    with open("output/raw_script.txt", "r", encoding="utf-8") as f:
        script_text = f.read()

    scenes = parse_screenplay(script_text)

    with open("output/parsed_script.json", "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=2, ensure_ascii=False)

    print(f" Parsed {len(scenes)} scenes. Output saved to output/parsed_script.json")
