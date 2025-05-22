# script_utils/ner_tagger.py
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    props = [ent.text for ent in doc.ents if ent.label_ in ("PRODUCT", "WORK_OF_ART", "ORG")]
    return list(set(props))

# script_utils/ner_tagger.py

