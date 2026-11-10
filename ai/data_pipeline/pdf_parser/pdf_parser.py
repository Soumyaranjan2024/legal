from pathlib import Path
import pymupdf
from ai.config.settings import settings
from ai.data_pipeline.ocr.ocr import extract_text_using_ocr


def extract_pdf_text(pdf_path: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    Identifies pages that may require OCR.
    """

    file_path = Path(pdf_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file is not a PDF.")

    pages = []
    full_text = []

    try:
        with pymupdf.open(file_path) as document:

            if document.is_encrypted:
                raise ValueError("PDF is password-protected.")

            metadata = document.metadata

            for page_number, page in enumerate(document, start=1):

                text = page.get_text("text").strip()

                pages.append({
                    "page_number": page_number,
                    "text": text,
                    "needs_ocr": len(text) < settings.OCR_MIN_TEXT_LENGTH
                })

                full_text.append(text)

            return {
                "file_name": file_path.name,
                "page_count": len(document),
                "metadata": metadata,
                "pages": pages,
                "full_text": "\n".join(full_text)
            }

    except (FileNotFoundError, ValueError):
        raise

    except Exception as error:
        raise RuntimeError(
            f"Failed to extract PDF text: {error}"
        ) from error


def extract_pdf_text_with_ocr(pdf_path: str) -> dict:
    """
    Extract normal PDF text first.
    Use OCR only on pages with insufficient extracted text.
    """

    result = extract_pdf_text(pdf_path)

    ocr_pages = [
        page["page_number"]
        for page in result["pages"]
        if page["needs_ocr"]
    ]

    if not ocr_pages:
        result["ocr_used"] = False
        return result

    ocr_result = extract_text_using_ocr(
        pdf_path,
        page_numbers=ocr_pages
    )

    ocr_text_map = {
        page["page_number"]: page["text"]
        for page in ocr_result["pages"]
    }

    for page in result["pages"]:
        if page["page_number"] in ocr_text_map:
            page["text"] = ocr_text_map[page["page_number"]]
            page["needs_ocr"] = False

    result["full_text"] = "\n".join(
        page["text"] for page in result["pages"]
    )

    result["ocr_used"] = True

    return result