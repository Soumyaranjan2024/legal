from ai.data_pipeline.download.document_downloader import download_pdf
from pathlib import Path

print("REAL PDF DOWNLOAD TEST")

url = "https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf"

try:
    result = download_pdf(
        url=url,
        output_dir="datasets/raw",
        filename="it_act_2000_download_test.pdf",
        max_size_mb=50
    )

    file_path = Path(result)

    print("\nDOWNLOAD SUCCESSFUL")
    print("File:", file_path.name)
    print("Location:", file_path)
    print("File size:", file_path.stat().st_size, "bytes")
    print("PDF signature verified:", file_path.read_bytes()[:5] == b"%PDF-")

except Exception as error:
    print("\nDOWNLOAD FAILED")
    print(type(error).__name__, error)