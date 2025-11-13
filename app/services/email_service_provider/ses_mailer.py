import boto3, os, base64, mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from .base import BaseMailer
from app.core.config import settings
from email.utils import encode_rfc2231

class SESMailer(BaseMailer):
    def __init__(self):
        self.ses = boto3.client(
            "ses",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION,
        )
        self.sender = settings.AWS_FROM_EMAIL

    def send_email(self, receiver, subject, body, attachment_path):
        try:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = receiver

            msg.attach(MIMEText(body, "html"))
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read())
                filename = os.path.basename(attachment_path)
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=encode_rfc2231(filename, "utf-8")
                )
                msg.attach(part)

            response = self.ses.send_raw_email(
                Source=self.sender,
                Destinations=[receiver],
                RawMessage={"Data": msg.as_string()},
            )
            return "MessageId" in response
        except Exception as e:
            print(f"[SESMailer] Error sending to {receiver}: {e}")
            return False
