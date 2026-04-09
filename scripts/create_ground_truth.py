from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import time
import random
from tqdm import tqdm
from generate_question import generate_question

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["chunks"]

# Pick 50 random articleIDs
# Now pick 100 more articles
sampled_ids = random.sample(range(1, 2001), 100)

# For each article pick a random chunkID and fetch it
sample_docs = []
for article_id in sampled_ids:
    # Find how many chunks this article has
    max_chunk = collection.count_documents({"articleID": article_id})
    if max_chunk == 0:
        continue
    random_chunk_id = random.randint(1, max_chunk)
    doc = collection.find_one(
        {"articleID": article_id, "chunkID": random_chunk_id},
        {"_id": 0, "text": 1, "article": 1, "articleID": 1, "chunkID": 1}
    )
    if doc:
        sample_docs.append(doc)

print(f"Found {len(sample_docs)} chunks from 100 sampled articles")

with open("evaluation/ground_truth.json", "r", encoding="utf-8") as f:
    ground_truth = json.load(f)
#ground_truth = []
failed = []

for doc in tqdm(sample_docs):
    try:
        entry = generate_question(
            chunk=doc["text"],
            article=doc["article"],
            chunk_id=doc["chunkID"],
            article_id=doc["articleID"]
        )
        ground_truth.append(entry)
        time.sleep(2)
    except Exception as e:
        print(f"Failed for article '{doc['article']}': {e}")
        failed.append(doc["article"])

os.makedirs("evaluation", exist_ok=True)

with open("evaluation/ground_truth.json", "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, ensure_ascii=False, indent=2)

print(f"\nDone — {len(ground_truth)} questions saved to evaluation/ground_truth.json")
if failed:
    print(f"Failed: {len(failed)} chunks — {failed}")