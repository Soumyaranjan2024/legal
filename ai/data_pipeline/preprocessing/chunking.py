from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_legal_document(
    document: dict,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> list:
    """
    Divide legal documents into smaller chunks
    while preserving legal section boundaries.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            r"\n(?=CHAPTER\s+[IVXLCDM]+\b)",
            r"\n(?=\d+[A-Z]?\.\s)",
            "\n\n",
            "\n",
            " ",
            ""
        ],
        is_separator_regex=True,
        keep_separator=True
    )

    chunks = []

    for page in document["pages"]:

        text = page["text"].strip()

        if not text:
            continue

        page_chunks = splitter.split_text(text)

        for index, chunk in enumerate(page_chunks):

            chunks.append({
                "chunk_id": (
                    f"{document['file_name']}"
                    f"_page_{page['page_number']}"
                    f"_chunk_{index + 1}"
                ),
                "text": chunk,
                "metadata": {
                    "source": document["file_name"],
                    "page_number": page["page_number"],
                    "chunk_index": index + 1
                }
            })

    return chunks