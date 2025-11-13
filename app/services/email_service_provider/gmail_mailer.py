import smtplib, os, base64, mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .base import BaseMailer
from app.core.config import settings

class GmailMailer(BaseMailer):
    def __init__(self):
        self.sender = settings.GMAIL_EMAIL
        self.password = settings.GMAIL_APP_PASSWORD
        if not self.sender or not self.password:
            raise ValueError("Gmail credentials missing")

    def send_email(self, receiver, subject, body, attachment_path):
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = receiver
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            ctype, _ = mimetypes.guess_type(attachment_path)
            maintype, subtype = (ctype or "application/octet-stream").split("/", 1)

            with open(attachment_path, "rb") as f:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                msg.attach(part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"[GmailMailer] Error sending to {receiver}: {e}")
            return False
