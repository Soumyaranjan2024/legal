"""FastAPI application entrypoint for the Legal Information Retrieval System.

Run from the project root::

    uvicorn backend.app.main:app --reload --port 8000

Swagger documentation is available at ``/docs``.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import (
    admin,
    auth,
    cases,
    chat,
    documents,
    procedures,
    search,
    system,
    users,
)
from backend.app.core.config import config
from backend.app.core.logging_config import configure_logging, get_logger

logger = get_logger("backend.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise logging and ensure all ChromaDB collections exist."""

    configure_logging()

    from backend.app.db.chroma import (
        chat_history_collection,
        chunks_collection,
        documents_collection,
        users_collection,
    )

    for name, factory in [
        ("users", users_collection),
        ("chat_history", chat_history_collection),
        ("legal_documents", documents_collection),
        ("legal_chunks", chunks_collection),
    ]:
        try:
            factory()
            logger.info("ChromaDB collection ready: %s", name)
        except Exception as error:  # pragma: no cover - defensive
            logger.error("Failed to initialise collection %s: %s", name, error)

    if not config.llm_configured:
        logger.warning(
            "No LLM API key is set (XAI_API_KEY, GROQ_API_KEY or "
            "GEMINI_API_KEY) - chatbot answers will fail until configured."
        )
    else:
        logger.info(
            "LLM provider: %s (%s)",
            config.llm_provider,
            config.llm_model,
        )

    logger.info("Legal IR API started (version %s)", config.VERSION)

    yield

    logger.info("Legal IR API shutting down.")


app = FastAPI(
    title="Legal Information Retrieval System API",
    description=(
        "AI-powered retrieval and explanation of Indian legal information. "
        "Powered by Grok (xAI), BGE/E5 embeddings and ChromaDB. "
        "This system provides legal information, not professional legal advice."
    ),
    version=config.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return a consistent JSON body for unexpected errors."""

    logger.exception("Unhandled error on %s %s", request.method, request.url.path)

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


@app.get("/", tags=["System"])
def root() -> dict:
    """Basic service information."""

    return {
        "name": "Legal Information Retrieval System API",
        "version": config.VERSION,
        "docs": "/docs",
        "disclaimer": (
            "This platform provides legal information, not professional "
            "legal advice."
        ),
    }


for router in [
    system.router,
    auth.router,
    users.router,
    chat.router,
    search.router,
    documents.router,
    cases.router,
    procedures.router,
    admin.router,
]:
    app.include_router(router, prefix=config.API_PREFIX)
