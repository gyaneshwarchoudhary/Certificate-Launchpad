# app/services/file_service.py
import os
from typing import Set
from fastapi import UploadFile
from werkzeug.utils import secure_filename

async def save_upload_file(upload_file: UploadFile, destination: str) -> None:
    """
    Save an UploadFile (async) to destination path.
    """
    os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
    try:
        with open(destination, "wb") as f:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
    finally:
        await upload_file.close()

async def save_template_file(template: UploadFile, save_dir: str = ".") -> str:
    """
    Save template image to disk. Returns saved path.
    Raises ValueError for invalid templates.
    """
    if not template or not template.filename:
        raise ValueError("Template file required")

    filename = secure_filename(template.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("Template must be an image (png/jpg)")

    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    await save_upload_file(template, path)
    return path

def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in allowed_extensions
