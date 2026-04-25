"""
This files takes test queries, and then performs retrieval from db.
Retrieval is done with all sensible permutations of db and query embedding model.
All results are stored in a .json file in evaluation folder, which can later be used to 
evaluate the quality of the retrieval based on the models used for document and query embeddings. 
"""
from search_qg import search
import json

PERMUTATIONS = [
    {"collection": "chunks",    "model": "voyage-4-large"},
    {"collection": "chunks",    "model": "voyage-4"},
    {"collection": "chunks",    "model": "voyage-4-lite"},
    {"collection": "chunks_v4", "model": "voyage-4"},
    {"collection": "chunks_v4", "model": "voyage-4-lite"},
    {"collection": "chunks_v4_lite", "model": "voyage-4-lite"},
]

with open("evaluation/ground_truth_court.json", "r", encoding="utf-8") as f:
    ground_truth = json.load(f)

#TEST_QUERIES = [entry["question"] for entry in ground_truth]

all_results = []

counter=0
for gt in ground_truth:
    
    for p in PERMUTATIONS:
        result = search(gt["question"], collection=p["collection"], model=p["model"])
        #all_results.append(result)
        all_results.append({
            "question":          gt["question"],
            #"expected_articleID": gt["articleID"],
            "expected_chunkID":   gt["chunkID"],
            #"expected_article":   gt["article"],
            "collection":         p["collection"],
            "embedding_model":    p["model"],
            "results":            result["results"]
        })
        print(f"✓ query='{gt['question']}' | collection={p['collection']} | model={p['model']}")
    
    if(counter>75):
        break
    counter+=1

with open("evaluation/raw_results_qg_test.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\nDone — {len(all_results)} results saved to evaluation/raw_results_qg.json")