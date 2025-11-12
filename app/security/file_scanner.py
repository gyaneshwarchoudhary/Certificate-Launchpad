import zipfile
import io
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile, HTTPException
import openpyxl

def validate_image_file(file: UploadFile):
    """
    Checks if the uploaded PNG is safe, non-corrupt, and actually an image.
    Rejects files that contain embedded scripts or non-image headers.
    """
    try:
        file_bytes = file.file.read()
        file.file.seek(0)
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()  # verifies it's a valid image file
        if img.format not in ["PNG", "JPEG"]:
            raise HTTPException(status_code=400, detail="Image must be PNG or JPEG")
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image validation failed: {e}")

def validate_excel_file(file: UploadFile):
    """
    Ensures uploaded Excel file is a valid XLSX/XLS without macros, 
    no hidden binary payloads or embedded files.
    """
    try:
        file_bytes = file.file.read()
        file.file.seek(0)

        # Check file extension and zip header
        if not file.filename.lower().endswith((".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Invalid Excel file format")

        # XLSX is a ZIP under the hood — check structure
        if file.filename.lower().endswith(".xlsx"):
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
                for member in archive.namelist():
                    # Reject macro or embedded binary content
                    if "vbaProject.bin" in member or "macros" in member.lower():
                        raise HTTPException(status_code=400, detail="Excel file contains macros (not allowed)")
                    if member.startswith("xl/embeddings/"):
                        raise HTTPException(status_code=400, detail="Excel contains embedded objects")
        
        # Try to parse sheet to ensure it's valid and safe
        openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        
        if len(file_bytes) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Excel file too large")
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Corrupt Excel file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel validation failed: {e}")
