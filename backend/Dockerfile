# Legal Information Retrieval System - FastAPI backend
# Build context must be the PROJECT ROOT so the shared `ai/` package and the
# bundled legal PDFs are available:
#   docker build -f backend/Dockerfile -t lirs-backend .

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf-cache

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

# Bundle the legal source PDFs and build the ChromaDB knowledge base into the
# image so the deployed service is queryable immediately. The build script is
# best-effort: it never fails the image build, and the embedding model cache is
# reused at runtime (HF_HOME above).
COPY datasets/raw/ datasets/raw/
ENV UPLOAD_DIRECTORY=/app/datasets/raw \
    CHROMA_PERSIST_DIRECTORY=/app/ai/storage/chroma_db \
    TESSERACT_CMD=/usr/bin/tesseract
RUN mkdir -p ai/storage/chroma_db \
    && python -m ai.scripts.build_vector_database \
    && rm -rf datasets/processed

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

# Bind to Render's $PORT when provided, else default to 8000.
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
