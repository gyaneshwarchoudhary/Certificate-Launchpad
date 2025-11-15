# Certificate-Launchpad

_A Production-Grade FastAPI + Celery + Redis Application_

---

## 📌 Overview

This project is a **scalable, secure, and production-ready certificate automation system** built with **FastAPI**, **Celery**, and **Redis**. It enables organizations to automatically generate personalized certificates from Excel sheets and send them via multiple email providers (Resend, Gmail SMTP, AWS SES), with real-time progress tracking and robust background task handling.

The application solves the repetitive and error-prone process of manually generating certificates and sending them individually. It provides an automated pipeline with preview, validation, asynchronous processing, and a dashboard summarizing successful and failed email deliveries.

---

## 🎯 Key Objectives

- Automate certificate creation from a template image and recipient list
- Enable users to preview certificates before final submission
- Support multiple email providers: **Resend**, **Gmail**, and **AWS SES**
- Run certificate generation & email sending as **asynchronous Celery jobs**
- Provide real-time progress tracking and a detailed results dashboard
- Enforce strict **file validation & security scanning** for Excel and PNG uploads
- Use **temporary in-project files** during preview to avoid disk bloat
- Implement **scheduled cleanup** for unused temp files using Celery Beat
- Build a scalable, Dockerized architecture for production deployment

---

## 🚀 Features

### ✔ FastAPI Web Application

- Responsive forms (data entry)
- Preview page for certificate visualization
- Process tracking page
- Summary dashboard page (success & failed recipients)

### ✔ Certificate Generation

- PNG/JPEG template support
- Custom font support (Roboto, OpenSans, Arial, Times New Roman)
- Dynamic text placement based on user-defined coordinates
- Output in **PDF format**

### ✔ Email Sending (User-Selectable Provider)

- **Resend API**
- **Gmail SMTP (App Password required)**
- **AWS SES (verified sender emails)**
- Provider chosen from UI
- Pluggable mailer architecture (easy to add more providers)

### ✔ File Validation & Security

- Validate PNG/JPG structure
- Validate Excel integrity
- Detect:
  - corrupt files
  - macro-enabled Excel files
  - embedded malware objects
- Reject oversized or invalid files
- Sanitize filenames
- Prevents server-side template injection
- Prevents malicious Excel uploads

### ✔ Asynchronous Processing (Celery)

- Runs long-running tasks in background (certificate generation + email sending)
- Uses Redis as broker & backend
- Reports progress via task meta updates
- Dashboard results delivered instantly after completion

### ✔ Temporary File Handling

- Preview uses **temporary files stored inside `/temp`**
- Temporary files are NOT written to permanent storage
- Permanent files saved ONLY after final confirmation

### ✔ Scheduled Cleanup (Celery Beat)

- Auto-deletes temp files older than 60 minutes
- Prevents disk bloat
- Runs in a separate Beat container

### ✔ Production-Ready Deployment

- Dockerized architecture
- Containers:
  - FastAPI app
  - Redis
  - Celery Worker
  - Celery Beat
- Easily deployable on:
  - DigitalOcean / Hetzner VPS
  - AWS EC2 / Lightsail
  - Docker Swarm
  - Kubernetes

---

## 🧱 Project Architecture

```
project_root/
│
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── api/routes/              # API routes
│   ├── services/                # certificate, email, file logic
│   ├── tasks/                   # celery tasks (worker & beat)
│   ├── utils/                   # validators, fonts mapping
│   ├── security/                # file scanning/malware checks
│   ├── schemas/                 # Pydantic form models
│   ├── core/config.py           # environment config
│   ├── templates/               # Jinja2 HTML templates
│   ├── static/                  # static files
│
├── certificates/                # generated certificate PDFs
├── uploads/                     # permanent uploaded sheets/templates
├── temp/                        # temporary preview files
│
├── Dockerfile                   # app container
├── docker-compose.yaml          # multi-container stack
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠 Tech Stack

**Backend**

- FastAPI
- Celery (async task execution)
- Redis (broker + result backend)
- Pydantic

**Certificate Generation**

- Pillow (PIL)

**Excel Processing**

- Pandas
- OpenPyXL

**Email Providers**

- Resend API
- Gmail SMTP
- AWS SES

**Deployment**

- Docker + Docker Compose
- Nginx (optional reverse proxy)
- Traefik (optional)

---

## ⚙️ Environment Variables

Create a `.env` file using `.env.example` as reference:

```env
# App directories
UPLOAD_FOLDER=uploads
CERT_DIR=certificates
TEMP_DIR=temp

# Email Providers
RESEND_API_KEY=your_resend_key
FROM_EMAIL=your_from_email

GMAIL_EMAIL=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_app_password

AWS_ACCESS_KEY=your_aws_key
AWS_SECRET_KEY=your_aws_secret
AWS_REGION=us-east-1
AWS_FROM_EMAIL=verified@yourdomain.com

# Redis for Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

## 🚀 Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/gyaneshwarchoudhary/Certificate-Launchpad.git
cd certificate-automation
```

### 2. Create & fill `.env`

```bash
cp .env.example .env
```

### 3. Install dependencies (optional non-docker)

```bash
pip install -r requirements.txt
```

---

## 🐳 Run with Docker (Recommended)

### 1. Build & start the entire stack

```bash
docker-compose up --build -d
```

### 2. Access the app

```
http://localhost:8000
```

---

## ⚡ Celery Services in Docker

### Celery Worker

```bash
docker-compose logs -f celery_worker
```

### Celery Beat

```bash
docker-compose logs -f celery_beat
```

### Redis

```bash
docker exec -it redis redis-cli
```

```bash
docker-compose up -d
```

## 🧹 Automatic Cleanup

A scheduled Celery Beat job deletes old temp files:

- **Directory:** `/temp`
- **Default retention:** 60 minutes
- **Purpose:** Prevents disk bloat from discarded previews

You can adjust retention in: `app/tasks/cleanup_tasks.py`

---

## ⚠️ Caveats

- Gmail SMTP has strict rate limits (use only for small batches)
- AWS SES requires domain or sender verification
- Ensure Redis volume persists if using production workloads
- Make sure `/uploads`, `/certificates`, `/temp` have write permissions
- Large Excel files may slow down processing — scale Celery workers if needed
- If using Docker, ensure your temp directory is **mounted** if persistence is required

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.
