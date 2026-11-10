import json
from pathlib import Path


def convert_to_json(data: dict, output_path: str = None) -> str:
    """
    Convert legal document metadata into JSON format.

    Args:
        data: Structured legal document metadata.
        output_path: Optional path to save the JSON file.

    Returns:
        JSON formatted string.
    """

    if not isinstance(data, dict):
        raise TypeError("Input data must be a dictionary.")

    try:
        json_data = json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"JSON conversion failed: {error}"
        ) from error

    if output_path is not None:

        file_path = Path(output_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            json_data,
            encoding="utf-8"
        )

    return json_data