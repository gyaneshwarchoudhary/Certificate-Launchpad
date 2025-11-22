# Certificate-Launchpad

**Production-grade certificate automation with FastAPI, Celery, and Redis**

Eliminate manual certificate generation. Upload a template and recipient list, preview output, then deploy async batch processing with real-time tracking and delivery confirmation across multiple email providers.

---

## Live Demonstration

https://github.com/user-attachments/assets/f939e520-a50f-4fca-8711-01e9b2a4b0f4


Complete walkthrough of certificate generation, preview system, async processing, email delivery, and results dashboard. Demonstrates full functionality in local Docker environment.

---

## Why This Exists

Manual certificate workflows fail at scale. This system automates the entire pipeline: template + Excel → personalized PDFs → validated delivery with failure tracking.

**Core value:** Transform hours of manual work into minutes of automated processing with zero human intervention after upload.

---

## What It Does

### Certificate Generation
- PNG/JPEG template support with custom fonts (Roboto, OpenSans, Arial, Times New Roman)
- Dynamic text placement via user-defined coordinates
- PDF output with validation

### Email Delivery (Multi-Provider)
- **Resend API** – Modern transactional email
- **Gmail SMTP** – App password authentication
- **AWS SES** – Enterprise-grade delivery
- Provider selection at runtime
- Pluggable architecture for additional providers

### Security & Validation
- PNG/JPG structure verification
- Excel integrity checks
- Macro-enabled file detection
- Malware object scanning
- Filename sanitization
- Template injection prevention

### Async Processing (Celery + Redis)
- Background job execution for certificate generation + email dispatch
- Real-time progress tracking via task metadata
- Instant dashboard delivery on completion

### File Management
- Preview mode: temporary files in `/temp` (60-minute auto-purge via Celery Beat)
- Production mode: permanent storage in `/uploads` and `/certificates`
- Scheduled cleanup prevents disk bloat

---

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌────────────────┐
│   FastAPI   │────▶│  Redis   │◀────│ Celery Worker  │
│     App     │     │  Broker  │     │  + Beat Sched. │
└─────────────┘     └──────────┘     └────────────────┘
```

**Component roles:**
- **FastAPI:** Web interface + API endpoints
- **Redis:** Task queue + result backend
- **Celery Worker:** Certificate generation + email sending
- **Celery Beat:** Scheduled file cleanup

---

## Project Structure

```
project_root/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── api/routes/              # API endpoints
│   ├── services/                # Certificate, email, file logic
│   ├── tasks/                   # Celery tasks (worker + beat)
│   ├── utils/                   # Validators, font mapping
│   ├── security/                # File scanning, malware checks
│   ├── schemas/                 # Pydantic models
│   ├── core/config.py           # Environment config
│   ├── templates/               # Jinja2 HTML
│   └── static/                  # CSS/JS assets
├── certificates/                # Generated PDFs
├── uploads/                     # Excel sheets + templates
├── temp/                        # Preview files (auto-purged)
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | FastAPI |
| Task Queue | Celery |
| Message Broker | Redis |
| Image Processing | Pillow (PIL) |
| Excel Parsing | Pandas, OpenPyXL |
| Email Providers | Resend, Gmail SMTP, AWS SES |
| Validation | Pydantic |

---

## Quick Start

### Local Deployment

```bash
# Clone repository
git clone https://github.com/gyaneshwarchoudhary/Certificate-Launchpad.git
cd certificate-automation

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up --build -d

# Access application
# http://localhost:8000
```

### Environment Configuration

**Required variables:**

```env
# Directories
UPLOAD_FOLDER=uploads
CERT_DIR=certificates
TEMP_DIR=temp

# Email providers (configure at least one)
RESEND_API_KEY=your_resend_key
FROM_EMAIL=your_from_email

GMAIL_EMAIL=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_app_password

AWS_ACCESS_KEY=your_aws_key
AWS_SECRET_KEY=your_aws_secret
AWS_REGION=us-east-1
AWS_FROM_EMAIL=verified@yourdomain.com

# Celery + Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

## Production Deployment

### Infrastructure Requirements
- **Memory:** 512MB minimum (3 concurrent services)
- **Storage:** Persistent Redis (not ephemeral)
- **Architecture:** Distributed task processing (incompatible with free-tier platforms like Render/Railway)

### Supported Platforms
- AWS ECS / EC2 / Lightsail
- DigitalOcean App Platform / Droplets
- Hetzner Cloud
- Any VPS with Docker support

**Cost estimate:** $10-15/month (managed) | $5/month (VPS)

---

## Service Management

### Monitor Celery Worker
```bash
docker-compose logs -f celery_worker
```

### Monitor Celery Beat
```bash
docker-compose logs -f celery_beat
```

### Access Redis CLI
```bash
docker exec -it redis redis-cli
```

### Restart services
```bash
docker-compose restart
```

---

## Operational Constraints

**Gmail SMTP:** Strict rate limits—use only for small batches (<100 emails/day)  
**AWS SES:** Requires domain/sender verification before production use  
**Redis:** Must persist data—configure volume mounts for production  
**Permissions:** Ensure `/uploads`, `/certificates`, `/temp` directories have write access  
**Scaling:** Large Excel files (>1000 rows) require additional Celery workers  
**Docker volumes:** Mount `/temp` if preview persistence is required across container restarts

---

## Automatic Cleanup

**Celery Beat task:** Deletes preview files older than 60 minutes from `/temp`

Configure retention period in: `app/tasks/cleanup_tasks.py`

---

## Contributing

Open an issue before submitting major changes. Pull requests must include tests and documentation updates.
