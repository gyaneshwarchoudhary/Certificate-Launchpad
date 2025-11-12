# app/services/certificate_service.py
import os
import re
import pandas as pd
from typing import Iterable, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from app.services.email_service import send_mail
from app.core.config import settings
from app.utils.validators import check_email

def make_certificate(
    name: str,
    template_file: str,
    font_file: str,
    starting_position: Optional[Iterable[int]] = (100, 100),
    out_dir: str = None,
) -> str:
    """
    Create certificate PDF from PNG template and return path to saved certificate (PDF).
    """
    out_dir = out_dir or settings.CERT_DIR
    os.makedirs(out_dir, exist_ok=True)

    img = Image.open(template_file).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # choose font size heuristically
    font_size = 96
    font = ImageFont.truetype(font_file, font_size)

    # shorten if too long (simple approach)
    if len(name) > 40:
        name_text = name[:37] + "..."
    else:
        name_text = name

    # draw text
    draw.text(tuple(starting_position), name_text, fill=(0, 0, 0), font=font)

    # create white background and save as PDF
    background = Image.new("RGB", img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)

    # sanitize filename
    safe_name = re.sub(r'[<>:"/\\|?*\t\n\r]', "_", name).strip()
    filename = os.path.join(out_dir, f"{safe_name}.pdf")
    background.save(filename, "PDF", resolution=100.0)
    return filename

# def process_excel_file(filepath: str, template_path: str, font_path: str, cords_data: Tuple[int, int], body: str, subject: str):
#     """
#     Process rows in an Excel file and generate/email certificates.
#     filepath may be a path or a URL; we assume path here.
#     """
#     try:
#         xls = pd.ExcelFile(filepath, engine="openpyxl")
#     except Exception as e:
#         print("Failed to open excel:", e)
#         return

#     for sheet in xls.sheet_names:
#         df = xls.parse(sheet)
#         # Expect two columns: name, email
#         for _, row in df.iterrows():
#             try:
#                 recipient_name = str(row[0]).strip()
#                 recipient_email = str(row[1]).strip()
#             except Exception:
#                 continue

#             if not check_email(recipient_email):
#                 print(f"Skipping invalid email: {recipient_email}")
#                 continue

#             cert = make_certificate(recipient_name, template_path, font_path, cords_data, out_dir=settings.CERT_DIR)
#             if cert:
#                 success = False
#                 try:
#                     success = send_mail(recipient_email, cert, subject=subject or f"Certificate for {recipient_name}", body=body or "")
#                 except Exception as e:
#                     print(f"Email error for {recipient_email}: {e}")
#                 if success:
#                     print(f"Sent certificate to {recipient_email}")
#     # optionally remove uploaded files
#     try:
#         os.remove(filepath)
#     except Exception:
#         pass
