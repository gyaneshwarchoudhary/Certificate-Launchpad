# app/api/routes/certificate_routes.py
import os
from app.tasks.certificate_tasks import process_excel_file
import pandas as pd
from fastapi import APIRouter, Request, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse,JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.file_service import save_template_file, allowed_file, save_upload_file
from app.services.certificate_service import make_certificate
from app.utils.fonts import get_font_path
from app.core.config import settings
from celery.result import AsyncResult
from app.celery_app import celery
from app.schemas.certificate_form import CertificateForm
from app.security.file_scanner import validate_image_file, validate_excel_file


router = APIRouter(tags=["certificate"])
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("data.html", {"request": request})

@router.post("/submit-data", response_class=HTMLResponse)
async def submit_data(request: Request, sheet: UploadFile, template: UploadFile):


    form_data = await request.form()
    try:
        validated_form = CertificateForm(**form_data)
        print(f"validated_form.model_dump()==={validated_form.model_dump()}")
    except Exception as e:
        return templates.TemplateResponse("data.html", {"request": request, "error": f"Invalid input: {e}"})

    # Validate uploaded files
    try:
        validate_excel_file(sheet)
        validate_image_file(template)
    except HTTPException as e:
        return templates.TemplateResponse("data.html", {"request": request, "error": e.detail})
    finally:
        # Reset file pointers for later reading
        sheet.file.seek(0)
        template.file.seek(0)

    cords = [float(x) for x in validated_form.cords.split(",")]
    fonts = validated_form.fonts

    if not sheet or not allowed_file(sheet.filename, settings.ALLOWED_EXTENSIONS):
        return templates.TemplateResponse("data.html", {"request": request, "error": "Invalid sheet file"})

    filename = f"{int(pd.Timestamp.now().timestamp())}_{sheet.filename}"
    sheet_path = os.path.join(settings.UPLOAD_FOLDER, filename)
    await save_upload_file(sheet, sheet_path)

    try:
        template_path = await save_template_file(template, save_dir=".")
        font_path = get_font_path(fonts)
        certificate_path = make_certificate(
            "Sample Name",
            template_path,
            font_path,
            tuple(cords),
            out_dir=settings.CERT_DIR,
        )
    except Exception as e:
        print("here in exception")
        return templates.TemplateResponse("data.html", {"request": request, "error": str(e)})

    return templates.TemplateResponse(
        "preview.html",
        {
            "request": request,
            "form": validated_form.model_dump(),
            "sheetpath": sheet_path,
            "templatepath": template_path,
            "certificate": certificate_path,
        },
    )

@router.post("/confirm", response_class=HTMLResponse)
async def confirm_send(request: Request):
    form = await request.form()
    subject = form.get("subject", "")
    body = form.get("body", "")
    cords = form.get("cords", "0,0")
    fonts = form.get("fonts", "")
    sheet_path = form.get("sheet")
    template_path = form.get("template")
    service= form.get('service')

    print(f"------------------------------service:{service}")

    try:
        cords_data = tuple(int(x) for x in cords.split(","))
    except Exception:
        return templates.TemplateResponse("preview.html", {"request": request, "error": "Invalid cords"})
    
    # enqueue background Celery task
    task = process_excel_file.delay(
        filepath=sheet_path,
        template_path=template_path,
        font_name=fonts,
        cords_data=cords_data,
        body=body,
        subject=subject,
        service=service,
     )

    return templates.TemplateResponse("progress.html", {"request": request, "task_id": task.id})

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
