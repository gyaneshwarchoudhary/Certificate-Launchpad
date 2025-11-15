# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    CERT_DIR = os.getenv("CERT_DIR", "certificates")
    FONT_DIR = os.getenv("FONT_DIR", os.path.join("app", "fonts"))
    TEMP_DIR = os.getenv("TEMP_DIR", "temp") 
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "xlsx,xls,png").split(","))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    AWS_FROM_EMAIL = os.getenv("AWS_FROM_EMAIL")
    AWS_ACCESS_KEY= os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY= os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND= os.getenv("CELERY_RESULT_BACKEND")
settings = Settings()
