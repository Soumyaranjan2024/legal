"""Embedding service using BGE or E5 models via Sentence Transformers.

The same compatible model is used for indexing document chunks and for
encoding user questions, as required for meaningful semantic retrieval.
"""

from typing import Optional

from ai.config.settings import settings

# BGE models are used with an instruction prefix for queries.
_BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# E5 models require distinct prefixes for passages and queries.
_E5_PASSAGE_PREFIX = "passage: "
_E5_QUERY_PREFIX = "query: "


class EmbeddingService:
    """Generate embeddings for legal documents and user queries."""

    _model_cache = {}

    def __init__(self, model_name: Optional[str] = None):

        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None

    @property
    def model(self):
        """Lazily load and cache the sentence-transformer model."""

        if self._model is None:

            from sentence_transformers import SentenceTransformer

            if self.model_name not in self._model_cache:
                self._model_cache[self.model_name] = (
                    SentenceTransformer(self.model_name)
                )

            self._model = self._model_cache[self.model_name]

        return self._model

    def _is_e5(self) -> bool:
        return "e5" in self.model_name.lower()

    def encode_documents(self, texts: list, batch_size: int = 32) -> list:
        """Generate embeddings for document chunks."""

        if not texts:
            return []

        if self._is_e5():
            texts = [_E5_PASSAGE_PREFIX + text for text in texts]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def encode_query(self, query: str) -> list:
        """Generate an embedding for a user query."""

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if self._is_e5():
            query_text = _E5_QUERY_PREFIX + query
        else:
            query_text = _BGE_QUERY_PREFIX + query

        embedding = self.model.encode(
            query_text,
            normalize_embeddings=True,
        )

        return embedding.tolist()
