# script_utils/pdf_extractor.py

from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"
    return full_text

# Usage Example
if __name__ == "__main__":
    pdf_path = "LM.pdf"  # Replace with the correct path if needed
    text = extract_text_from_pdf(pdf_path)
    with open("output/raw_script.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Script text extraction complete.")
