import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ai.rag.rag_pipeline import LegalRAGPipeline


def main():

    print("\nInitializing Legal RAG Pipeline...\n")

    rag = LegalRAGPipeline(top_k=5)

    question = (
        "What is the legal recognition of electronic "
        "records under Section 4 of the Information "
        "Technology Act, 2000?"
    )

    print("QUESTION:")
    print(question)

    print("\nGenerating answer...\n")

    result = rag.generate_answer(question)

    print("=" * 60)
    print("RETRIEVED SOURCES")
    print("=" * 60)

    for source in result["sources"]:
        print(f"\nDocument: {source['document']}")
        print(f"Page: {source['page']}")
        print(f"Distance: {source['distance']:.4f}")

    print("\n" + "=" * 60)
    print("GENERATED LEGAL ANSWER")
    print("=" * 60)

    print(result["answer"])

    print("\n" + "=" * 60)
    print("RAG TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()