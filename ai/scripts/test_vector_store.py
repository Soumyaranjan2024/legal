from ai.data_pipeline.preprocessing.document_preprocessor import (
    preprocess_document
)

from ai.data_pipeline.preprocessing.chunking import (
    chunk_legal_document
)

from ai.rag.embeddings.embedding_service import (
    EmbeddingService
)

from ai.rag.vector_database.vector_store import (
    LegalVectorStore
)


PDF_PATH = "datasets/raw/it_act_2000.pdf"


def main():

    print("\n1. Preprocessing legal document...")

    document = preprocess_document(PDF_PATH)

    print("Document:", document["file_name"])

    print("\n2. Creating chunks...")

    chunks = chunk_legal_document(document)

    print("Total chunks:", len(chunks))

    print("\n3. Generating embeddings...")

    embedding_service = EmbeddingService()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_service.encode_documents(texts)

    print("Total embeddings:", len(embeddings))

    print("\n4. Connecting to ChromaDB...")

    vector_store = LegalVectorStore()

    stored = vector_store.add_documents(
        chunks,
        embeddings
    )

    print("Chunks stored:", stored)

    print("\n5. Testing semantic retrieval...")

    query = "What is the legal recognition of electronic records?"

    query_embedding = embedding_service.encode_query(query)

    results = vector_store.search(
        query_embedding,
        top_k=3
    )

    print("\nUser query:", query)

    for index, result in enumerate(
        results["documents"][0],
        start=1
    ):

        print(f"\nResult {index}:")
        print("Text:", result[:400])

        print(
            "Metadata:",
            results["metadatas"][0][index - 1]
        )

        print(
            "Distance:",
            results["distances"][0][index - 1]
        )

    print("\nTotal chunks in ChromaDB:",
          vector_store.count_documents())

    print("\nCHROMADB TEST COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()