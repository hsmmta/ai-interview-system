# ai-assistant-fastapi

FastAPI bridge service for the Java/JSP website.

## Endpoints

- `GET /health`
- `POST /api/v1/questions/generate`
- `POST /api/v1/evaluate`

## Quick Start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

