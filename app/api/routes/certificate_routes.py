# app/api/routes/certificate_routes.py
import os
import tempfile
import pandas as pd
import shutil
from app.tasks.certificate_tasks import process_excel_file
import pandas as pd
from fastapi import APIRouter, Request, UploadFile, HTTPException
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.certificate_service import make_certificate
from app.utils.fonts import get_font_path
from app.core.config import settings
from celery.result import AsyncResult
from app.celery_app import celery
from app.schemas.certificate_form import CertificateForm
from app.security.file_scanner import validate_image_file, validate_excel_file


router = APIRouter(tags=["certificate"])
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})

@router.get('/uploads',response_class=HTMLResponse)
async def upload_page(request:Request):
    return templates.TemplateResponse('uploads.html',{"request":request})


@router.post("/submit-data", response_class=HTMLResponse)
async def submit_data(request: Request, sheet: UploadFile, template: UploadFile):
    form_data = await request.form()
    
    # -------- Validate using Pydantic --------
    try:
        validated_form = CertificateForm(**form_data)
    except Exception as e:
        return templates.TemplateResponse(
            "uploads.html", {"request": request, "error": str(e)}
        )

    # -------- Validate files (security scanning) --------
    try:
        validate_excel_file(sheet)
        validate_image_file(template)
    except HTTPException as e:
        return templates.TemplateResponse(
            "uploads.html", {"request": request, "error": e.detail}
        )
    finally:
        sheet.file.seek(0)
        template.file.seek(0)

    cords = tuple(int(x) for x in validated_form.cords.split(","))
    fonts = validated_form.fonts

   # Ensure temp dir exists
    os.makedirs(settings.TEMP_DIR, exist_ok=True)

    # Store Excel temporarily
    temp_sheet = tempfile.NamedTemporaryFile(
        delete=False, suffix=".xlsx", dir=settings.TEMP_DIR
    )
    temp_sheet.write(await sheet.read())
    temp_sheet.flush()

    # Store template temporarily
    temp_template = tempfile.NamedTemporaryFile(
        delete=False, suffix=".png", dir=settings.TEMP_DIR
    )
    temp_template.write(await template.read())
    temp_template.flush()
    # Generate preview certificate
    font_path = get_font_path(fonts)
    if font_path == "":
         return templates.TemplateResponse(
            "uploads.html", {"request": request, "error": e.detail}
        )
    certificate = make_certificate(
        name="Sample Name",
        template_file=temp_template.name,
        font_file=font_path,
        starting_position=cords,
        out_dir=settings.CERT_DIR,
    )
    print(f"\n\n=====================================")
    print(temp_template)
    print(temp_sheet)
    print(f"=====================================\n\n")
    return templates.TemplateResponse(
        "preview.html",
        {
            "request": request,
            "form": validated_form.model_dump(),
            "temp_sheet": temp_sheet.name,
            "temp_template": temp_template.name,
            "certificate": certificate,
        },
    )

# routes for confirmation of data
@router.post("/confirm", response_class=HTMLResponse)
async def confirm_send(request: Request):
    form = await request.form()
    subject = form.get("subject", "")
    body = form.get("body", "")
    cords = form.get("cords", "0,0")
    fonts = form.get("fonts", "")
    service= form.get('service')
    temp_sheet = form.get("temp_sheet")
    temp_template = form.get("temp_template")
    
 # Create final filenames
    timestamp = str(int(pd.Timestamp.now().timestamp()))
    final_sheet_path = os.path.join(settings.UPLOAD_FOLDER, f"{timestamp}_sheet.xlsx")
    final_template_path = os.path.join(settings.UPLOAD_FOLDER, f"{timestamp}_template.png")

    # Make sure upload folder exists
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    # Move temp → permanent
    shutil.move(temp_sheet, final_sheet_path)
    shutil.move(temp_template, final_template_path)
    try:
        cords_data = tuple(int(x) for x in cords.split(","))
    except Exception:
        return templates.TemplateResponse("preview.html", {"request": request, "error": "Invalid cords"})
    
    # enqueue background Celery task
    task = process_excel_file.delay(
        filepath=final_sheet_path,
        template_path=final_template_path,
        font_name=fonts,
        cords_data=cords_data,
        body=body,
        subject=subject,
        service=service,
     )

    return templates.TemplateResponse("progress.html", {"request": request, "task_id": task.id})

# route for progress.html to show the progress
@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """AJAX endpoint polled by frontend to check task progress."""
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state == "PENDING":
        return JSONResponse({"state": "PENDING", "percent": 0})
    elif task_result.state == "PROGRESS":
        return JSONResponse({"state": "PROGRESS", **task_result.info})
    elif task_result.state == "SUCCESS":
        return JSONResponse({"state": "SUCCESS", "result": task_result.result})
    elif task_result.state == "FAILURE":
        return JSONResponse({"state": "FAILURE", "error": str(task_result.info)})
    else:
        return JSONResponse({"state": str(task_result.state)})

#route for dashborad
@router.get("/dashboard/{task_id}", response_class=HTMLResponse)
async def dashboard(request: Request, task_id: str):
    """Show summary dashboard for a finished task."""
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state != "SUCCESS":
        return templates.TemplateResponse(
            "dashboard.html", {"request": request, "summary": None, "error": "Task not complete yet"}
        )

    summary = task_result.result.get("summary", {})
    return templates.TemplateResponse("dashboard.html", {"request": request, "summary": summary})
