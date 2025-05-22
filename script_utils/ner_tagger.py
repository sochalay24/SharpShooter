# script_utils/ner_tagger.py
import spacy
import re

nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    props = [ent.text for ent in doc.ents if ent.label_ in ("PRODUCT", "WORK_OF_ART", "ORG")]
    return list(set(props))

def extract_known_characters_from_actions(action_lines, known_characters):
    """
    Return a list of known character names that appear in the action lines.
    """
    text = " ".join(action_lines).upper()
    found = []
    for character in known_characters:
        # Whole word match to avoid partial false positives
        pattern = r'\b' + re.escape(character) + r'\b'
        if re.search(pattern, text):
            found.append(character)
    return list(set(found))

