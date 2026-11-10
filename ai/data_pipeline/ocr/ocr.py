from pathlib import Path
import os
import pymupdf
import pytesseract
from PIL import Image
import io

from ai.config.settings import settings

# Use a configured Tesseract binary when available, otherwise rely on PATH.
TESSERACT_PATH = settings.TESSERACT_CMD

if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_using_ocr(pdf_path: str, page_numbers=None) -> dict:
    """
    Extract text from selected PDF pages using OCR.

    page_numbers uses 1-based page numbering.
    If None, all pages are processed.
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

            selected_pages = (
                range(len(document))
                if page_numbers is None
                else [number - 1 for number in page_numbers]
            )

            for index in selected_pages:

                if index < 0 or index >= len(document):
                    raise ValueError(f"Invalid page number: {index + 1}")

                page = document[index]

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )

                text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                ).strip()

                pages.append({
                    "page_number": index + 1,
                    "text": text
                })

                full_text.append(text)

        return {
            "file_name": file_path.name,
            "page_count": len(pages),
            "pages": pages,
            "full_text": "\n".join(full_text)
        }

    except Exception as error:
        raise RuntimeError(
            f"OCR extraction failed: {error}"
        ) from error