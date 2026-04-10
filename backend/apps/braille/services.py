# backend/apps/braille/services.py

from .utils import braille_map

def convert_text_to_braille(text: str):
    result = []
    for ch in text:
        pattern = braille_map.get(ch, [0, 0, 0, 0, 0, 0])
        result.append({"char": ch, "pattern": pattern})
    return result