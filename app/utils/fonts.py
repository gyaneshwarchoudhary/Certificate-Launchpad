# app/utils/fonts.py
import os
from app.core.config import settings

FONT_MAP = {
    "roboto": "Roboto-Regular.ttf",
    "georgia": "Georgia.ttf",
    "opensans": "OpenSans-Regular.ttf",
    "timesnewroman": "TimesNewRoman.ttf",
    "arial": "Arial.ttf",
}

def get_font_path(font_name: str) -> str:
    if not font_name:
        raise ValueError("Font name required")
    key = font_name.strip().lower()
    filename = FONT_MAP.get(key)
    if not filename:
        raise ValueError(f"Unsupported font '{font_name}'. Supported: {', '.join(FONT_MAP.keys())}")
    path = os.path.join(settings.FONT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Font file not found: {path}")
    return path
