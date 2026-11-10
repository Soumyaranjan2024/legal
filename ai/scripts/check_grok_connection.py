from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI, APIStatusError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("XAI_API_KEY")

if not api_key:
    print("ERROR: XAI_API_KEY not found in .env")
    raise SystemExit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)

try:
    response = client.models.list()

    print("Connection successful!")
    print("Available models:")

    for model in response.data:
        print("-", model.id)

except APIStatusError as error:
    print("API request failed.")
    print("Status:", error.status_code)
    print("Details:", error.response.text)

except Exception as error:
    print("Unexpected error:", repr(error))