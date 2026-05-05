from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
from collections import defaultdict
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["chunks"]

print("Fetching all documents...")
docs = list(collection.find({}, {"_id": 1, "article": 1, "chunk_index": 1}))
print(f"Total documents: {len(docs)}")

# Group document IDs by article title
article_groups = defaultdict(list)
for doc in docs:
    article_groups[doc.get("article", "")].append(doc)

print(f"Unique articles: {len(article_groups)}")

# Sort chunks within each article by chunk_index
for title in article_groups:
    article_groups[title].sort(key=lambda d: d.get("chunk_index", 0))

# Build bulk update operations
bulk_ops = []
article_id = 0

for title, chunks in article_groups.items():
    article_id += 1
    for chunk_id, doc in enumerate(chunks, start=1):
        bulk_ops.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {"articleID": article_id, "chunkID": chunk_id}}
        ))

    if len(bulk_ops) >= 500:
        collection.bulk_write(bulk_ops)
        print(f"  Written {len(bulk_ops)} ops...")
        bulk_ops = []

if bulk_ops:
    collection.bulk_write(bulk_ops)
    print(f"  Written remaining {len(bulk_ops)} ops...")

print(f"\nDone — {article_id} articles, {len(docs)} documents updated")