# script_utils/parser.py
import re
import unicodedata

# Normalization helper
def normalize_line(s: str) -> str:
    s = unicodedata.normalize('NFKC', s)   # normalize accents/compatibility
    s = s.replace("\u00A0", " ")           # NBSP -> space
    s = s.replace("–", "-").replace("—", "-")  # en/em dashes
    s = re.sub(r"\s+", " ", s)             # collapse multiple spaces
    return s.strip()

# Regex to detect proper scene headings
SCENE_HEADING_RE = re.compile(
    r'^\s*(\d+[A-Z]*)?\.?\s*'              # optional number e.g. 12A.
    r'(INT|EXT|INT/EXT|EXT/INT|I/E)\.?\s+' # INT/EXT/I/E
    r'(.+?)'                               # location
    r'(?:\s*[-\.]\s*(DAY|NIGHT|EVENING|MORNING|DAWN|DUSK))?' # time of day
    r'(\s*\d+[A-Z]*)?\s*$',                # trailing number
    re.IGNORECASE
)

CHARACTER_RE = re.compile(r'^[A-Z][A-Z0-9\s\.\-\'()]{0,40}$')

BLACKLIST = {
    "CUT TO", "FADE IN", "FADE OUT", "THE END",
    "DISSOLVE TO", "MATCH CUT", "SMASH CUT",
    "BACK TO SCENE", "SUPER", "TITLE", "HARD CUT TO"
}

def extract_location_and_time(heading):
    h = normalize_line(heading)
    m = SCENE_HEADING_RE.match(h)
    if m:
        loc = m.group(3).strip().upper()
        tod = (m.group(4) or "UNKNOWN").upper()
        return loc, tod
    return "UNKNOWN", "UNKNOWN"

def parse_screenplay(script_text):
    scenes = []
    scene = None
    scene_count = 0

    # Pre-normalize lines
    lines = [normalize_line(l) for l in script_text.splitlines() if normalize_line(l)]

    for line in lines:
        # Detect scene headings
        if SCENE_HEADING_RE.match(line):
            if scene:
                scenes.append(scene)
            scene_count += 1
            location, time_of_day = extract_location_and_time(line)
            scene = {
                "scene_number": scene_count,
                "heading": line,
                "location": location,
                "time_of_day": time_of_day,
                "characters": [],
                "actions": []
            }
            continue

        # Detect characters
        if scene and CHARACTER_RE.match(line):
            tok_count = len(line.split())
            if 1 <= tok_count <= 3:
                up = line.rstrip(':').upper()
                if up not in BLACKLIST and not up.endswith("TO"):
                    if up not in scene["characters"]:
                        scene["characters"].append(up)
                    continue

        # Otherwise: treat as action
        if scene:
            scene["actions"].append(line)

    if scene:
        scenes.append(scene)

    return scenes

# Debug mode
if __name__ == "__main__":
    with open("output/raw_script.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    scenes = parse_screenplay(raw_text)
    print(f"Parsed {len(scenes)} scenes.")
    for s in scenes[:5]:  # show first 5
        print(s["heading"], s["characters"], s["time_of_day"])
