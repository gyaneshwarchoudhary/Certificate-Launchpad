# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes.certificate_routes import router as certificate_router
from app.api.routes.healthcheck import router as health_router
from app.core.config import settings
import os

app = FastAPI(title="Certificate Generator")

# Ensure directories exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.CERT_DIR, exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)

# mount static and certs
app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")
app.mount("/certificates", StaticFiles(directory=settings.CERT_DIR), name="certificates")

#-- Jinga2 template engine
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

# include routers
app.include_router(certificate_router)
app.include_router(health_router)
