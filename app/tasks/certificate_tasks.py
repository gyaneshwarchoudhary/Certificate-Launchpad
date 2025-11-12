from app.celery_app import celery
from app.services.certificate_service import make_certificate
from app.services.email_service import send_mail
from app.utils.validators import check_email
from app.core.config import settings
from app.utils.fonts import get_font_path
import pandas as pd
import os

@celery.task(bind=True, name="tasks.process_excel_file", max_retries=3)
def process_excel_file(self, filepath, template_path, font_name, cords_data, body, subject):
    """
    Celery background task: generate & email certificates.
    Tracks progress and returns summary.
    """
    summary = {"success": [], "failed": []}
    try:
        font_path = get_font_path(font_name)
        xls = pd.ExcelFile(filepath, engine="openpyxl")
        all_rows = sum(len(xls.parse(sheet)) for sheet in xls.sheet_names)
        processed = 0

        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            for _, row in df.iterrows():
                processed += 1
                try:
                    recipient_name = str(row[0]).strip()
                    recipient_email = str(row[1]).strip()
                except Exception:
                    summary["failed"].append("Invalid row format")
                    continue

                if not check_email(recipient_email):
                    summary["failed"].append(f"Invalid email: {recipient_email}")
                    continue

                try:
                    cert = make_certificate(
                        name=recipient_name,
                        template_file=template_path,
                        font_file=font_path,
                        starting_position=tuple(cords_data),
                        out_dir=settings.CERT_DIR,
                    )
                    if cert:
                        sent = send_mail(
                            receiver=recipient_email,
                            certificate_filepath=cert,
                            subject=subject or f"Certificate for {recipient_name}",
                            body=body or "",
                        )
                        if sent:
                            summary["success"].append(recipient_email)
                        else:
                            summary["failed"].append(recipient_email)
                except Exception as e:
                    summary["failed"].append(f"{recipient_email}: {str(e)}")

                # Update progress
                percent = round((processed / all_rows) * 100, 2)
                self.update_state(
                    state="PROGRESS",
                    meta={"current": processed, "total": all_rows, "percent": percent},
                )

    # Cleanup input files
        for f in (filepath, template_path):
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as cleanup_error:
                print(f"⚠️ Could not delete temp file {f}: {cleanup_error}")
            

            return {"status": "DONE", "summary": summary}

    except Exception as e:
        raise self.retry(exc=e, countdown=10)

