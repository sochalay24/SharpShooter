import re
from datetime import datetime, timedelta
from collections import defaultdict

def extract_scene_root(heading):
    # Extract the root number from scene heading, e.g., "2A", "2B" → "2"
    match = re.match(r"^\s*(\d+)", heading)
    return match.group(1) if match else "0"

def group_and_sort_scenes(scenes):
    grouped = defaultdict(list)
    for scene in scenes:
        root = extract_scene_root(scene["heading"])
        key = (root, scene["location"], scene["time_of_day"])
        grouped[key].append(scene)

    # Sort group keys by root scene number (as int), location, then time of day
    sorted_groups = sorted(grouped.items(), key=lambda k: (int(k[0][0]), k[0][1], k[0][2]))
    return sorted_groups

def generate_schedule(scenes):
    grouped_scenes = group_and_sort_scenes(scenes)
    schedule = []
    current_day = 1
    current_time = datetime.strptime("08:00", "%H:%M")
    hours_today = 0
    max_hours_per_day = 10

    for (scene_root, location, time_of_day), scene_list in grouped_scenes:
        for scene in scene_list:
            duration_hours = 2 if len(scene["characters"]) > 2 else 1

            if current_time.strftime("%H:%M") == "13:00":
                current_time += timedelta(hours=1)
                hours_today += 1

            if hours_today + duration_hours > max_hours_per_day:
                current_day += 1
                current_time = datetime.strptime("08:00", "%H:%M")
                hours_today = 0

            schedule.append({
                "day": current_day,
                "start_time": current_time.strftime("%H:%M"),
                "scene_heading": scene["heading"],
                "location": scene["location"],
                "time_of_day": scene["time_of_day"],
                "characters": scene["characters"],
                "estimated_duration": f"{duration_hours} hour(s)"
            })

            current_time += timedelta(hours=duration_hours)
            hours_today += duration_hours

    return schedule
