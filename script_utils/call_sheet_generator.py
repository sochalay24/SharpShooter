# script_utils/call_sheet_generator.py
from collections import defaultdict


def generate_call_sheets(schedule):
    call_sheets = defaultdict(lambda: {"actors": set(), "scenes": []})

    for item in schedule:
        day = item["day"]
        call_sheets[day]["actors"].update(item["characters"])
        call_sheets[day]["scenes"].append(item["scene_heading"])

    for day in call_sheets:
        call_sheets[day]["actors"] = list(call_sheets[day]["actors"])

    return call_sheets
