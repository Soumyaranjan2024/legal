# Legal Information Retrieval System - FastAPI backend
# Build context must be the PROJECT ROOT so the shared `ai/` package is available:
#   docker build -f backend/Dockerfile -t lirs-backend .

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies: Tesseract for OCR + Poppler for pdfplumber + build tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        poppler-utils \
        libgl1 \
        libglib2.0-0 \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (AI layer + backend).
COPY ai/requirements.txt ai/requirements.txt
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r ai/requirements.txt \
    && pip install -r backend/requirements.txt

# Copy application code.
COPY ai/ ai/
COPY backend/ backend/

# Directories for uploads and the persistent ChromaDB store.
RUN mkdir -p datasets/raw ai/storage/chroma_db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
