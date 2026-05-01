"""
Local file-based image storage.
Saves generated images to Backend/static/images/ and returns
a localhost URL that FastAPI serves via StaticFiles.
"""
import os
from pathlib import Path

# Absolute path to the static/images directory (relative to this file)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → Backend/
STATIC_DIR = _BASE_DIR / "static" / "images"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

BACKEND_BASE_URL = "http://localhost:8000"


def save_image_locally(image_bytes: bytes, file_name: str) -> str:
    """
    Saves image bytes to Backend/static/images/<file_name>
    and returns the public localhost URL.
    """
    dest = STATIC_DIR / file_name
    with open(dest, "wb") as f:
        f.write(image_bytes)
    url = f"{BACKEND_BASE_URL}/static/images/{file_name}"
    print(f"Image saved locally: {url}")
    return url
