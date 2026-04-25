from google import genai
from google.genai import types
import pathlib
from dotenv import load_dotenv
import os

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Retrieve and encode the PDF byte
filepath = pathlib.Path('data_qg/lilia_harcaqnnutyun.pdf')

PROMPT = """Extract all Armenian text from this PDF.

Rules:
- Exctract content as it is, do not change the structure
- Do not translate or summarize — extract exact Armenian text
"""
response = client.models.generate_content(
  model="gemini-3-flash-preview",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      PROMPT])
#print(response.text)

output_path = pathlib.Path("output.txt")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(response.text)