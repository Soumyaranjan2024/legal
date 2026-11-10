from ai.llm.grok.client import GrokClient

client = GrokClient()

response = client.generate_response(
    "Explain Section 4 of the Information Technology Act, 2000 in simple language."
)

output_path = "ai/scripts/grok_response.txt"

with open(output_path, "w", encoding="utf-8") as file:
    file.write(response)

print("Grok API test successful!")
print("Response saved to:", output_path)