# scripts/ocr_pdf.py
from google import genai
from google.genai import types
from pydantic import BaseModel
import pathlib
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

INPUT_DIR  = "D:\capstone_data\data/pdf_batches"
OUTPUT_DIR = "D:\capstone_data\data/ocr_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TextChunk(BaseModel):
    heading:     str
    text:        str
    page_number: int

class BatchContent(BaseModel):
    chunks: list[TextChunk]

PROMPT = """Extract all Armenian text from this PDF.

Rules:
- Split content into paragraph-level chunks
- For each chunk include the page number it appears on
- For each chunk include the heading above it (e.g. "Ներածական մաս", "Պատճառաբանական մաս")
- If no heading exists above a chunk use empty string "" for heading
- Do not translate or summarize — extract exact Armenian text
- Return structured output only"""

batch_files = sorted(pathlib.Path(INPUT_DIR).glob("*.pdf"))
print(f"Found {len(batch_files)} batch files")

# Skip already processed batches
already_done = {f.stem for f in pathlib.Path(OUTPUT_DIR).glob("*.json")}
print(f"Already processed: {len(already_done)} batches")

all_chunks = []

# Load already completed chunks
for done_file in sorted(pathlib.Path(OUTPUT_DIR).glob("*.json")):
    with open(done_file, "r", encoding="utf-8") as f:
        all_chunks.extend(json.load(f)["chunks"])

for batch_file in batch_files:
    if batch_file.stem in already_done:
        print(f"Skipping {batch_file.name} (already done)")
        continue

    print(f"Processing {batch_file.name}...")
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(
                    data=batch_file.read_bytes(),
                    mime_type="application/pdf"
                ),
                PROMPT
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BatchContent
            )
        )

        batch_data = json.loads(response.text)
        chunks = batch_data["chunks"]
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks extracted")

        out_file = f"{OUTPUT_DIR}/{batch_file.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"chunks": chunks}, f, ensure_ascii=False, indent=2)

        time.sleep(1)

    except Exception as e:
        print(f"  Failed: {e}")

# Save combined output
with open("data/ocr_combined.json", "w", encoding="utf-8") as f:
    json.dump({"chunks": all_chunks}, f, ensure_ascii=False, indent=2)

print(f"\nDone — {len(all_chunks)} total chunks saved to data/ocr_combined.json")