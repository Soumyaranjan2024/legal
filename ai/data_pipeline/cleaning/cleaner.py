import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean extracted legal document text
    while preserving legal meaning and structure.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove null characters
    text = text.replace("\x00", "")

    # Remove unwanted control characters
    text = "".join(
        char for char in text
        if char in "\n\t" or unicodedata.category(char)[0] != "C"
    )

    # Remove extra spaces and tabs within lines
    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in text.split("\n")
    ]

    # Remove excessive blank lines
    cleaned_lines = []
    previous_blank = False

    for line in lines:

        if not line:
            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True

        else:
            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


def clean_extracted_pages(pages: list) -> list:
    """
    Clean extracted text page by page.
    Preserve page numbers and other metadata.
    """

    cleaned_pages = []

    for page in pages:

        cleaned_pages.append({
            **page,
            "text": clean_text(page.get("text", ""))
        })

    return cleaned_pages