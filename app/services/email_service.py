# app/services/email_service.py
import os
import base64
from app.core.config import settings
import resend
import time

def send_mail(receiver: str, certificate_filepath: str, from_email: str = None, subject: str = "", body: str = "") -> bool:
    """
    Send mail using Resend. Requires RESEND_API_KEY in env.
    Returns True if email send is assumed successful, False on failure.
    """
    api_key = settings.RESEND_API_KEY
    if not api_key:
        # Fail fast: can't send without API key
        raise ValueError("RESEND_API_KEY not set")

    from_email = from_email or settings.FROM_EMAIL
    resend.api_key = api_key

    try:
        with open(certificate_filepath, "rb") as f:
            content = f.read()
        attachment_b64 = base64.b64encode(content).decode("utf-8")
        params = {
            "from": from_email,
            "to": [receiver],
            "subject": subject,
            "html": f"<p>{body}</p>",
            "attachments": [
                {
                    "filename": os.path.basename(certificate_filepath),
                    "content": attachment_b64,
                }
            ],
        }
        resend.Emails.send(params)
        try:
            time.sleep(0.5)
            os.remove(certificate_filepath)
        except:
            pass 
        return True
    except Exception as e:
        # in production, log the exception
        print("send_mail error:", e)
        return False
