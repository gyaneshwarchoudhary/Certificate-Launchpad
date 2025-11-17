import os
import time
from celery import shared_task
from app.core.config import settings

MAX_AGE_SECONDS = 3600  # 60 minutes

@shared_task(name="tasks.cleanup_temp_files")
def cleanup_temp_files():
    temp_dir = settings.TEMP_DIR
    now = time.time()
    deleted = []

    if not os.path.exists(temp_dir):
        return {"deleted": [], "error": "temp dir does not exist"}

    for file in os.listdir(temp_dir):
        path = os.path.join(temp_dir, file)

        if not os.path.isfile(path):
            continue

        age = now - os.path.getmtime(path)
        print(age, MAX_AGE_SECONDS)
        if age > MAX_AGE_SECONDS:
            try:
                os.remove(path)
                deleted.append(file)
            except Exception as e:
                pass

    return {"deleted": deleted}
