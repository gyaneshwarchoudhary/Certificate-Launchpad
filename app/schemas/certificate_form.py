from pydantic import BaseModel, Field, field_validator
from fastapi import UploadFile
from typing import Optional
import re

class CertificateForm(BaseModel):
    cords: str = Field(..., description="Comma-separated X,Y coordinates, e.g. '324.4, 332'")
    fonts: str = Field(..., description="Font name like roboto, opensans, etc.")
    subject: Optional[str] = Field(default="Your Certificate")
    body: Optional[str] = Field(default="Please find your certificate attached."),
    service:str = Field(...,description="service is required")
    sheet: Optional[UploadFile] = None
    template: Optional[UploadFile] = None

    @field_validator("cords")
    def validate_cords(cls, v):
        # Updated regex to allow float numbers in coordinates
        if not re.match(r"^\s*\d+(\.\d+)?,\s*\d+(\.\d+)?\s*$", v):
            raise ValueError("Invalid cords format. Expected format: 'X,Y' with numeric values, e.g. '324.4, 332'")
        return v

    @field_validator("fonts")
    def validate_fonts(cls, v):
        allowed_fonts = {"roboto", "opensans", "timesnewroman", "arial"}
        if v.lower().strip() not in allowed_fonts:
            raise ValueError(f"Unsupported font '{v}'. Allowed: {', '.join(allowed_fonts)}")
        return v.lower().strip()

    @field_validator("subject")
    def validate_subject(cls, v):
        # Ensure the subject isn't empty and doesn't exceed a reasonable length
        if not v or len(v.strip()) == 0:
            raise ValueError("Subject cannot be empty")
        if len(v) > 100:
            raise ValueError("Subject is too long. Maximum length is 100 characters.")
        return v.strip()

    class Config:
        extra = "ignore"
