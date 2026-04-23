# scripts/embed_court_case.py
import json
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm
import os
import time
import pathlib

load_dotenv()

vo     = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["court_case"]

# Clear existing data
collection.delete_many({})
print("Cleared existing court_case documents")

# Load all batch files in order
OCR_DIR = "data_qg/ocr_output"
batch_files = sorted(pathlib.Path(OCR_DIR).glob("*.json"))
print(f"Found {len(batch_files)} batch files")

all_chunks = []
for batch_file in batch_files:
    with open(batch_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        all_chunks.extend(data["chunks"])

print(f"Total chunks loaded: {len(all_chunks)}")

# Build documents with IDs and heading-prepended text for embedding
docs = []
for chunk_id, item in enumerate(all_chunks):
    heading = item.get("heading", "").strip()
    text    = item.get("text", "").strip()

    if len(text) < 30:
        continue

    # Prepend heading to text for embedding — improves retrieval quality
    if heading:
        embed_text = f"[Բաժին: {heading}] {text}"
    else:
        embed_text = text

    docs.append({
        "chunkID":     chunk_id,
        "documentID":  1,
        "text":        text,        # stored as-is for display
        "embed_text":  embed_text,  # heading + text used for embedding
        "heading":     heading,
        "page_number": item.get("page_number", 0),
        "source":      "court_case.pdf",
        "language":    "hy"
    })

print(f"Docs to embed: {len(docs)}")

# Embed and store in batches
BATCH_SIZE = 8
to_insert  = []

for i in tqdm(range(0, len(docs), BATCH_SIZE)):
    batch = docs[i:i + BATCH_SIZE]
    texts = [d["embed_text"] for d in batch]

    result = vo.embed(texts, model="voyage-4-large", input_type="document")

    for doc, vector in zip(batch, result.embeddings):
        to_insert.append({
            "chunkID":     doc["chunkID"],
            "documentID":  doc["documentID"],
            "text":        doc["text"],
            "heading":     doc["heading"],
            "page_number": doc["page_number"],
            "source":      doc["source"],
            "language":    doc["language"],
            "embedding":   vector
            # embed_text is not stored — only used for embedding
        })

    if len(to_insert) >= 200:
        collection.insert_many(to_insert)
        to_insert = []

    time.sleep(0.3)

if to_insert:
    collection.insert_many(to_insert)

print(f"\nDone — {collection.count_documents({})} documents inserted into court_case")