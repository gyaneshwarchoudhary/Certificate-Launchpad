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
