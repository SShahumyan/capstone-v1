from pymongo import MongoClient
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

collection = client["armenian_search"]["chunks"]

# --- Gemini client ---
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-embedding-2"

def get_embedding(text: str):
    response = genai_client.models.embed_content(
        model=MODEL,
        contents=text
    )
    return response.embeddings[0].values  # vector

# --- Process documents ---
batch_size = 50
docs = collection.find({}, {"text": 1})

batch = []

for doc in docs:
    text = doc.get("text", "")
    if not text:
        continue

    embedding = get_embedding(text)

    batch.append({
        "_id": doc["_id"],
        "embedding": embedding
    })

    # bulk update in batches
    if len(batch) >= batch_size:
        for item in batch:
            collection.update_one(
                {"_id": item["_id"]},
                {"$set": {"embedding": item["embedding"]}}
            )
        print(f"Updated {len(batch)} docs")
        batch = []

# final batch
for item in batch:
    collection.update_one(
        {"_id": item["_id"]},
        {"$set": {"embedding": item["embedding"]}}
    )

print("Done embedding all documents.")