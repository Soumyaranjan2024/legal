# Legal Information Retrieval System

An AI-powered platform for retrieving and explaining **Indian legal information** —
Acts, sections, and Supreme Court / High Court judgments — using a **RAG**
(Retrieval-Augmented Generation) architecture.

> **Disclaimer:** This platform provides **legal information, not professional legal advice**.
> Always consult a qualified lawyer for advice on a specific situation.

---

## Technology Stack

| Layer            | Technology                                                             |
| ---------------- | ---------------------------------------------------------------------- |
| Frontend         | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS            |
| Backend          | Python, FastAPI, Pydantic v2                                           |
| LLM              | **Grok API by xAI ONLY** (`https://api.x.ai/v1`)                       |
| Database         | **ChromaDB ONLY** (persistent local storage)                           |
| Embeddings       | BGE / E5 via Sentence Transformers                                     |
| PDF extraction   | PyMuPDF, pdfplumber                                                    |
| OCR              | Tesseract (PaddleOCR-compatible wrapper)                               |
| Architecture     | RAG                                                                    |
| Deployment       | Docker, docker-compose                                                 |
| Version control  | Git / GitHub                                                           |

No other database, LLM, or vector store is used anywhere in the project.

---

## Project Structure

```
LEGAL_INFROMATION_RETRIEVAL_SYSTEM/
├── ai/                        # ML / RAG layer (pipeline + retrieval + LLM)
│   ├── config/                # Central settings (reads .env)
│   ├── data_collection/       # Official-source & Kaggle collectors
│   ├── data_pipeline/         # PDF -> OCR -> clean -> Grok extract -> chunk -> embed
│   ├── llm/                   # Grok (xAI) client + answer validator
│   ├── rag/                   # Embeddings, retrieval, vector DB, prompts, pipeline
│   ├── security/              # Prompt-injection guardrails
│   └── scripts/               # build_vector_database, ingest, tests
├── backend/                   # FastAPI application
│   └── app/
│       ├── api/routes/        # auth, users, chat, search, cases, procedures,
│       │                      # documents, admin, system
│       ├── core/              # config, security, logging, rate limiting
│       ├── db/                # ChromaDB client + repositories
│       ├── schemas/           # Pydantic request/response models
│       └── services/          # Business logic (RAG, search, users, admin)
├── frontend/                  # Next.js application
│   └── src/
│       ├── app/               # Pages (home, auth, dashboard, chat, search,
│       │                      # cases, documents, procedures, history, admin)
│       ├── components/        # Reusable UI components
│       └── lib/               # API client, auth context, types
├── datasets/
│   ├── raw/                   # Uploaded / downloaded PDFs
│   └── processed/             # Structured JSON metadata
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Data Flow (RAG Pipeline)

```
PDF / HTML  →  text extraction  →  scanned-page detection  →  OCR (if needed)
   →  cleaning  →  preprocessing  →  Grok information extraction
   →  structured JSON  →  Pydantic validation  →  chunking
   →  BGE/E5 embeddings  →  ChromaDB (legal_chunks + legal_documents)

User question  →  embedding  →  ChromaDB semantic search (+ metadata filters)
   →  retrieved context  →  Grok answer generation  →  answer + sources + disclaimer
```

Grok is used **only** for information extraction and answer generation. It is never
allowed to invent legal facts or citations — unavailable fields are stored as
`null` / empty and validated with Pydantic.

---

## ChromaDB Collections

| Collection        | Purpose                                                         |
| ----------------- | --------------------------------------------------------------- |
| `legal_documents` | Document details, source metadata, serialized structured JSON   |
| `legal_chunks`    | Text chunks, embeddings, document IDs, page & legal metadata    |
| `users`           | User accounts (auth)                                            |
| `chat_history`    | Conversation messages per user                                  |

Only ChromaDB-supported scalar metadata types are stored; nested/list values are
serialized into the document body.

---

## Getting Started (local)

### 1. Backend

```powershell
# from the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ai/requirements.txt
pip install -r backend/requirements.txt

# Tesseract is required for scanned PDFs (Windows):
winget install --id UB-Mannheim.TesseractOCR

# Build the vector database from the PDFs in datasets/raw
python -m ai.scripts.build_vector_database

# Run the API
uvicorn backend.app.main:app --reload --port 8000
```

- API root: <http://localhost:8000>
- Swagger docs: <http://localhost:8000/docs>

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

- App: <http://localhost:3000>

### 3. Configuration

Copy `.env.example` to `.env` at the project root and set at least:

```env
XAI_API_KEY=your-xai-api-key-here
```

Keys used by the app: `XAI_API_KEY`, `GROK_MODEL`, `CHROMA_PERSIST_DIRECTORY`,
`EMBEDDING_MODEL`, `JWT_SECRET_KEY`, `NEXT_PUBLIC_API_URL`, `UPLOAD_DIRECTORY`.
**API keys are never exposed to the frontend or committed to Git.**

---

## Running with Docker

```powershell
cp .env.example .env      # then set XAI_API_KEY
docker compose up --build
```

- Backend → <http://localhost:8000> (Swagger at `/docs`)
- Frontend → <http://localhost:3000>

ChromaDB data and uploaded files persist in named Docker volumes.

---

## Key API Endpoints

| Method | Endpoint                          | Description                        |
| ------ | --------------------------------- | ---------------------------------- |
| POST   | `/api/auth/register`              | Register (first user becomes admin)|
| POST   | `/api/auth/login`                 | Obtain JWT access token            |
| GET    | `/api/auth/me`                    | Current user profile               |
| POST   | `/api/chat`                       | Ask the AI legal chatbot           |
| GET    | `/api/chat/conversations`         | List conversations                 |
| POST   | `/api/search`                     | Keyword / semantic / hybrid search |
| GET    | `/api/cases`                      | List legal cases & judgments       |
| GET    | `/api/procedures`                 | List legal procedures              |
| POST   | `/api/documents/upload`           | Upload a PDF for ingestion         |
| POST   | `/api/documents/ingest-url`       | Ingest a document from a URL       |
| GET    | `/api/admin/stats`                | Admin dashboard statistics         |
| GET    | `/api/system/status`              | ChromaDB / Grok / system status    |

---

## Security

- Passwords hashed with bcrypt (SHA-256 pre-hash).
- Signed JWT access tokens (HS256) — verified on every protected route.
- Role-based admin access.
- Rate limiting (login, chat, search).
- Upload validation (extension, size, PDF signature).
- Prompt-injection guardrails for uploaded document content.
- Grok API credentials kept strictly on the backend.

---

## Data Collection

- **Method A — Official sources:** India Code, Supreme Court of India, High Courts,
  eCourts, government sources. Website terms and access restrictions are respected;
  CAPTCHAs and restricted access are **not** bypassed.
- **Method B — Kaggle dataset:** the *SC Judgments India (1950–2024)* dataset can be
  uploaded and ingested locally.
- **Manual uploads:** PDFs can be uploaded through the Documents page/API.

All methods preserve source URLs, extract metadata, detect duplicates, handle
errors, and track processing status.
