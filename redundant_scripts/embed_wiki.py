"""
this is a code responsible for adding vectors to mongodb.
It adds contents from data/armenian_chunks.json currently.
"""
import voyageai
from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv
from tqdm import tqdm
import time

load_dotenv()

vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["chunks_v4_lite"]

# Clear previous data
# collection.delete_many({})
# print("Cleared old documents")

with open("data/armenian_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

BATCH_SIZE = 8
docs_to_insert = []

for i in tqdm(range(0, len(chunks), BATCH_SIZE)):
    batch = chunks[i:i + BATCH_SIZE]
    texts = [item["text"] for item in batch]

    result = vo.embed(texts, model="voyage-4-lite", input_type="document")

    for j, (item, vector) in enumerate(zip(batch, result.embeddings)):
        docs_to_insert.append({
            "text":        item["text"],
            "embedding":   vector,
            "article":     item["article"],
            "chunk_index": i + j,
            "source":      "wikipedia",
            "language":    "hy"
        })

    # Insert in batches of 200 to avoid memory buildup
    if len(docs_to_insert) >= 200:
        collection.insert_many(docs_to_insert)
        docs_to_insert = []

    time.sleep(0.3)

# Insert any remaining
if docs_to_insert:
    collection.insert_many(docs_to_insert)

print(f"Done — {collection.count_documents({})} documents in Atlas")