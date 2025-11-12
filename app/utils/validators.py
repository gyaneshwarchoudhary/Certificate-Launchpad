# app/utils/validators.py
import re

EMAIL_REGEX = re.compile(r"^[\w\.\-+]+@[\w\.\-]+\.\w{2,}$")

def check_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))
