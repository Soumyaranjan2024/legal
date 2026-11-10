from ai.data_pipeline.pdf_parser.pdf_parser import (
    extract_pdf_text_with_ocr
)

from ai.data_pipeline.cleaning.cleaner import (
    clean_extracted_pages
)


def preprocess_document(pdf_path: str) -> dict:
    """
    Extract PDF text, perform OCR when required,
    and clean the extracted content.
    """

    # Step 1: Extract PDF text and perform OCR if needed
    document = extract_pdf_text_with_ocr(pdf_path)

    # Step 2: Clean extracted text page by page
    cleaned_pages = clean_extracted_pages(
        document["pages"]
    )

    # Step 3: Combine cleaned pages
    cleaned_full_text = "\n".join(
        page["text"] for page in cleaned_pages
    )

    # Step 4: Return processed document
    return {
        "file_name": document["file_name"],
        "page_count": document["page_count"],
        "metadata": document["metadata"],
        "ocr_used": document["ocr_used"],
        "pages": cleaned_pages,
        "full_text": cleaned_full_text
    }