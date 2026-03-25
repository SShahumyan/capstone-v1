import voyageai
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from tqdm import tqdm
import time

load_dotenv()

vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["chunks"]

with open("data/armenian_texts.txt", "r", encoding="utf-8") as f:
    chunks = [p.strip() for p in f.read().split("\n\n") if len(p.strip()) > 10]

print(f"Loaded {len(chunks)} chunks")

BATCH_SIZE = 8
docs_to_insert = []

for i in tqdm(range(0, len(chunks), BATCH_SIZE)):
    batch = chunks[i:i + BATCH_SIZE]
    result = vo.embed(batch, model="voyage-4-large", input_type="document")
    
    for j, (text, vector) in enumerate(zip(batch, result.embeddings)):
        docs_to_insert.append({
            "text": text,
            "embedding": vector,
            "chunk_index": i + j,
            "source": "grqaser",
            "language": "hy"
        })
    
    time.sleep(0.3)

collection.insert_many(docs_to_insert)
print(f"Inserted {len(docs_to_insert)} documents")