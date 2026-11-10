import ssl
import certifi
import re
import urllib.request
import urllib.error

from pathlib import Path
from urllib.parse import urlparse, unquote


def download_pdf(
    url: str,
    output_dir: str = "datasets/raw",
    filename: str = None,
    max_size_mb: int = 50
) -> str:
    """
    Download and validate a publicly accessible PDF document.

    Args:
        url: Direct URL of the PDF.
        output_dir: Directory where the PDF will be saved.
        filename: Optional custom filename.
        max_size_mb: Maximum permitted download size.

    Returns:
        Path of the downloaded PDF.
    """

    # Validate URL
    if not isinstance(url, str) or not url.startswith(
        ("http://", "https://")
    ):
        raise ValueError(
            "A valid HTTP or HTTPS URL is required."
        )

    if max_size_mb <= 0:
        raise ValueError(
            "Maximum file size must be positive."
        )

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Extract filename from URL
    if filename is None:
        parsed_url = urlparse(url)
        filename = unquote(
            Path(parsed_url.path).name
        )

    if not filename:
        raise ValueError(
            "Could not determine the PDF filename."
        )

    # Sanitize filename
    filename = Path(filename).name

    filename = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        filename
    )

    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    destination = output_path / filename

    max_bytes = max_size_mb * 1024 * 1024

    # Prepare HTTP request
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "LegalDocumentResearchSystem/1.0"
        }
    )

    try:
        # Configure SSL using Certifi certificates
        ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

        # Download PDF
        with urllib.request.urlopen(
            request,
            timeout=30,
            context=ssl_context
        ) as response:

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            content_length = response.headers.get(
                "Content-Length"
            )

            # Check declared file size
            if content_length:

                if int(content_length) > max_bytes:
                    raise ValueError(
                        "PDF exceeds the maximum allowed size."
                    )

            data = bytearray()

            # Read file in chunks
            while True:

                chunk = response.read(8192)

                if not chunk:
                    break

                data.extend(chunk)

                if len(data) > max_bytes:
                    raise ValueError(
                        "Downloaded file exceeds the maximum size."
                    )

    except urllib.error.HTTPError as error:

        raise RuntimeError(
            f"HTTP download failed: "
            f"{error.code} {error.reason}"
        ) from error

    except urllib.error.URLError as error:

        raise RuntimeError(
            f"Unable to access URL: {error.reason}"
        ) from error

    # Verify PDF signature
    if not data.startswith(b"%PDF-"):

        raise ValueError(
            "Downloaded content is not a valid PDF. "
            f"Content-Type: {content_type}"
        )

    # Save verified PDF
    with destination.open("wb") as file:
        file.write(data)

    return str(destination)