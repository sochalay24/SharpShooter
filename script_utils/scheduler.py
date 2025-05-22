# script_utils/scheduler.py
from collections import defaultdict

def create_schedule(scenes):
    grouped = defaultdict(list)
    for scene in scenes:
        key = (scene["location"], scene["time"])
        grouped[key].append(scene)

    schedule = []
    start_hour = 8  # 8 AM start
    lunch_hour = 13  # 1 PM lunch
    night_start = 18  # 6 PM

    day = 1
    hour = start_hour

    for key, scene_group in grouped.items():
        for scene in scene_group:
            block = {
                "day": day,
                "time": f"{hour}:00",
                "scene": scene["heading"],
                "location": scene["location"],
                "characters": scene["characters"],
                "props": scene["props"],
                "duration": "2 hours"  # or calculate based on tokens/dialogue
            }
            schedule.append(block)
            hour += 2
            if hour == lunch_hour:
                hour += 1  # 1-hour lunch break
            if hour >= night_start:
                day += 1
                hour = start_hour

    return schedule
