"""Shared, lazily constructed AI-layer singletons.

The embedding model is expensive to load, so the RAG pipeline, retriever and
ingestion pipeline are created once per process and reused across requests.
"""

from typing import Optional

from ai.data_pipeline.ingestion_pipeline import LegalIngestionPipeline
from ai.rag.rag_pipeline import LegalRAGPipeline
from ai.rag.retrieval.retriever import LegalRetriever

_rag_pipeline: Optional[LegalRAGPipeline] = None
_retriever: Optional[LegalRetriever] = None
_ingestion_pipeline: Optional[LegalIngestionPipeline] = None


def get_rag_pipeline() -> LegalRAGPipeline:
    global _rag_pipeline

    if _rag_pipeline is None:
        _rag_pipeline = LegalRAGPipeline()

    return _rag_pipeline


def get_retriever() -> LegalRetriever:
    global _retriever

    if _retriever is None:
        _retriever = LegalRetriever()

    return _retriever


def get_ingestion_pipeline() -> LegalIngestionPipeline:
    global _ingestion_pipeline

    if _ingestion_pipeline is None:
        _ingestion_pipeline = LegalIngestionPipeline()

    return _ingestion_pipeline
