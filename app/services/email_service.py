from app.services.email_service_provider.resend_mailer import ResendMailer
from app.services.email_service_provider.gmail_mailer import GmailMailer
from app.services.email_service_provider.ses_mailer import SESMailer

def get_mailer(service: str):
    service = (service or "").lower()
    if service == "resend":
        return ResendMailer()
    elif service == "gmail":
        return GmailMailer()
    elif service == "ses":
        return SESMailer()
    else:
        raise ValueError(f"Unknown email service '{service}'")

def send_mail(receiver, certificate_filepath, service="resend", subject="", body=""):
    """
    Unified send_mail entrypoint — dispatches to chosen service.
    """
    try:
        mailer = get_mailer(service)
        return mailer.send_email(receiver, subject, body, certificate_filepath)
    except Exception as e:
        print(f"[send_mail] Fatal error using service '{service}': {e}")
        return False
