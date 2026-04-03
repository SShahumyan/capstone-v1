"""This file changes the entries in the db so that each entry will get article id and chunk id.
   article id and chunk id will form composite keys.
"""
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["chunks"]

print("Fetching documents...")
docs = list(collection.find(
    {"articleID": {"$exists": False}},
    {"_id": 1, "article": 1}
))

print(f"Documents to update: {len(docs)}")

if not docs:
    print("All documents already updated.")
    exit()

# Get the last updated document — both its articleID and article title
last = collection.find_one(
    {"articleID": {"$exists": True}},
    sort=[("articleID", -1)]
)

if last:
    current_article_id = last["articleID"]
    last_chunk_id = last["chunkID"]
    prev_article = last["article"]

    # If first unupdated doc is from the same article, continue its chunkID
    if docs[0]["article"] == prev_article:
        chunk_id = last_chunk_id  # will be incremented to last_chunk_id + 1 on first iteration
    else:
        current_article_id += 1
        chunk_id = 0  # will be incremented to 1 on first iteration
else:
    current_article_id = 0
    chunk_id = 0
    prev_article = None

bulk_ops = []

for doc in docs:
    title = doc.get("article", "")

    if title != prev_article:
        current_article_id += 1
        chunk_id = 1
        prev_article = title
    else:
        chunk_id += 1

    bulk_ops.append(UpdateOne(
        {"_id": doc["_id"]},
        {"$set": {"articleID": current_article_id, "chunkID": chunk_id}}
    ))

    if len(bulk_ops) == 500:
        collection.bulk_write(bulk_ops)
        print(f"  Written {len(bulk_ops)} ops...")
        bulk_ops = []

if bulk_ops:
    collection.bulk_write(bulk_ops)
    print(f"  Written {len(bulk_ops)} ops...")

print(f"\nDone — {len(docs)} documents updated")