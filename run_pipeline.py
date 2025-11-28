# run_pipeline.py

import json
import os
import tempfile
from io import BytesIO

from script_utils.call_sheet_generator import generate_call_sheets
from script_utils.pdf_extractor import extract_text_from_pdf
from script_utils.parser import parse_screenplay
from script_utils.scheduler import generate_schedule

def get_screenplay_pdf_path(data_dir="data"):
    """Return the most recently modified PDF inside the data directory."""
    pdf_candidates = [
        os.path.join(data_dir, file_name)
        for file_name in os.listdir(data_dir)
        if file_name.lower().endswith(".pdf")
    ]

    if not pdf_candidates:
        raise FileNotFoundError(
            f"No PDF files found in '{data_dir}'. Please add a screenplay PDF."
        )

    pdf_candidates.sort(key=lambda path: os.path.getmtime(path), reverse=True)
    return pdf_candidates[0]


def process_screenplay_from_pdf(pdf_path=None, pdf_bytes=None, output_dir="output"):
    """
    Process a screenplay PDF and generate all outputs.
    
    Args:
        pdf_path: Path to PDF file (if processing from file)
        pdf_bytes: Bytes of PDF file (if processing from upload)
        output_dir: Directory to save outputs
    
    Returns:
        dict: Contains 'scenes', 'schedule', and 'call_sheets'
    """
    # Handle PDF input (either from path or bytes)
    if pdf_bytes:
        # Save uploaded PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            pdf_path = tmp_file.name
    
    if not pdf_path:
        raise ValueError("Either pdf_path or pdf_bytes must be provided")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/call_sheets", exist_ok=True)
    
    # Clear old outputs
    _clear_output_directory(output_dir)
    
    # 1. Extract text from screenplay PDF
    script_text = extract_text_from_pdf(pdf_path)
    
    # 2. Parse scenes from the script text
    scenes = parse_screenplay(script_text)
    
    # 3. Save parsed scenes
    with open(f"{output_dir}/parsed_script.json", "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=2)
    
    # 4. Generate shooting schedule
    schedule = generate_schedule(scenes)
    
    # 5. Save schedule
    with open(f"{output_dir}/shooting_schedule.json", "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)
    
    # 6. Generate call sheets per day
    call_sheets = generate_call_sheets(schedule)
    
    # 7. Save each day's call sheet to its own file
    for day, data in call_sheets.items():
        with open(f"{output_dir}/call_sheets/day_{day}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    # Clean up temporary file if created from bytes
    if pdf_bytes and os.path.exists(pdf_path):
        os.unlink(pdf_path)
    
    return {
        "scenes": scenes,
        "schedule": schedule,
        "call_sheets": call_sheets
    }


def _clear_output_directory(output_dir="output"):
    """Clear old output files."""
    # Clear call sheets directory
    call_sheets_dir = f"{output_dir}/call_sheets"
    if os.path.exists(call_sheets_dir):
        for file in os.listdir(call_sheets_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(call_sheets_dir, file))
    
    # Clear main output files
    for file in ["parsed_script.json", "shooting_schedule.json"]:
        file_path = os.path.join(output_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)


# Command-line usage (backward compatibility)
if __name__ == "__main__":
    pdf_path = get_screenplay_pdf_path()
    result = process_screenplay_from_pdf(pdf_path=pdf_path)
    
    print("Parsed scenes saved to output/parsed_script.json")
    print("Shooting schedule saved to output/shooting_schedule.json")
    print("Call sheets saved to output/call_sheets/")