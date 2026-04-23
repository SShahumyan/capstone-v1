from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import time
import random
from tqdm import tqdm
from generate_question_qg import generate_question

load_dotenv()

mongo      = MongoClient(os.getenv("MONGODB_URI"))
collection = mongo["armenian_search"]["court_case"]
OUTPUT     = "evaluation/ground_truth_court.json"
TARGET     = 500

total = collection.count_documents({})
print(f"Total chunks in court_case: {total}")

all_chunk_ids = collection.distinct("chunkID")
sampled_ids   = random.sample(all_chunk_ids, min(TARGET, len(all_chunk_ids)))
print(f"Sampled {len(sampled_ids)} chunk IDs")

sample_docs = list(collection.find(
    {"chunkID": {"$in": sampled_ids}},
    {"_id": 0, "text": 1, "chunkID": 1, "documentID": 1}
))
print(f"Fetched {len(sample_docs)} documents")

os.makedirs("evaluation", exist_ok=True)

# Resume support
if os.path.exists(OUTPUT):
    with open(OUTPUT, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)
    done_ids = {entry["chunkID"] for entry in ground_truth}
    print(f"Resuming — {len(ground_truth)} entries already done")
else:
    ground_truth = []
    done_ids     = set()

failed = []

for doc in tqdm(sample_docs):
    if doc["chunkID"] in done_ids:
        continue

    try:
        entry = generate_question(
            chunk=doc["text"],
            chunk_id=doc["chunkID"],
            document_id=doc["documentID"]
        )
        ground_truth.append(entry)
        done_ids.add(doc["chunkID"])
        time.sleep(1)

        if len(ground_truth) % 50 == 0:
            with open(OUTPUT, "w", encoding="utf-8") as f:
                json.dump(ground_truth, f, ensure_ascii=False, indent=2)
            print(f"  Checkpoint — {len(ground_truth)} entries saved")

    except Exception as e:
        print(f"  Failed chunkID {doc['chunkID']}: {e}")
        failed.append(doc["chunkID"])

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, ensure_ascii=False, indent=2)

print(f"\nDone — {len(ground_truth)} questions saved to {OUTPUT}")
if failed:
    print(f"Failed {len(failed)} chunks: {failed}")