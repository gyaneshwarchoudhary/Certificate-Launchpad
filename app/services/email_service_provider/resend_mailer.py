import base64, os
import resend
from .base import BaseMailer
from app.core.config import settings

class ResendMailer(BaseMailer):
    def __init__(self):
        api_key = settings.RESEND_API_KEY
        if not api_key:
            raise ValueError("RESEND_API_KEY not set")
        resend.api_key = api_key
        self.from_email = settings.FROM_EMAIL

    def send_email(self, receiver, subject, body, attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")

            resend.Emails.send({
                "from": self.from_email,
                "to": [receiver],
                "subject": subject,
                "html": f"<p>{body}</p>",
                "attachments": [{"filename": os.path.basename(attachment_path), "content": content}],
            })
            return True
        except Exception as e:
            print(f"[ResendMailer] Error sending to {receiver}: {e}")
            return False
