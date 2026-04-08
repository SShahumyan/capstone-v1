import json
from collections import defaultdict

with open("evaluation/raw_results.json", "r", encoding="utf-8") as f:
    raw_results = json.load(f)

PERMUTATIONS = [
    {"collection": "chunks",         "model": "voyage-4-large"},
    {"collection": "chunks",         "model": "voyage-4"},
    {"collection": "chunks",         "model": "voyage-4-lite"},
    {"collection": "chunks_v4",      "model": "voyage-4"},
    {"collection": "chunks_v4",      "model": "voyage-4-lite"},
    {"collection": "chunks_v4_lite", "model": "voyage-4-lite"},
]

def evaluate(entries):
    total = len(entries)
    if total == 0:
        return None

    hit_at_1_chunk  = 0  # exact chunk match at rank 1
    hit_at_3_chunk  = 0  # exact chunk match in top 3
    hit_at_5_chunk  = 0  # exact chunk match in top 5
    hit_at_1_article  = 0  # correct article at rank 1
    hit_at_3_article  = 0  # correct article in top 3
    hit_at_5_article  = 0  # correct article in top 5
    reciprocal_ranks_chunk   = []
    reciprocal_ranks_article = []

    for entry in entries:
        exp_article_id = entry["expected_articleID"]
        exp_chunk_id   = entry["expected_chunkID"]
        results        = entry["results"]

        # --- chunk-level ---
        chunk_rank = None
        for r in results:
            if r["articleID"] == exp_article_id and r["chunkID"] == exp_chunk_id:
                chunk_rank = r["rank"]
                break

        if chunk_rank == 1: hit_at_1_chunk += 1
        if chunk_rank and chunk_rank <= 3: hit_at_3_chunk += 1
        if chunk_rank and chunk_rank <= 5: hit_at_5_chunk += 1
        reciprocal_ranks_chunk.append(1 / chunk_rank if chunk_rank else 0)

        # --- article-level ---
        article_rank = None
        for r in results:
            if r["articleID"] == exp_article_id:
                article_rank = r["rank"]
                break

        if article_rank == 1: hit_at_1_article += 1
        if article_rank and article_rank <= 3: hit_at_3_article += 1
        if article_rank and article_rank <= 5: hit_at_5_article += 1
        reciprocal_ranks_article.append(1 / article_rank if article_rank else 0)

    return {
        "total_queries": total,
        "chunk_level": {
            "hit@1":  round(hit_at_1_chunk  / total, 3),
            "hit@3":  round(hit_at_3_chunk  / total, 3),
            "hit@5":  round(hit_at_5_chunk  / total, 3),
            "MRR":    round(sum(reciprocal_ranks_chunk) / total, 3),
        },
        "article_level": {
            "hit@1":  round(hit_at_1_article  / total, 3),
            "hit@3":  round(hit_at_3_article  / total, 3),
            "hit@5":  round(hit_at_5_article  / total, 3),
            "MRR":    round(sum(reciprocal_ranks_article) / total, 3),
        }
    }

# Group entries by permutation
grouped = defaultdict(list)
for entry in raw_results:
    key = (entry["collection"], entry["embedding_model"])
    grouped[key].append(entry)

# Evaluate and print results
report = []
print(f"\n{'='*90}")
print(f"{'Permutation':<40} {'Level':<10} {'Hit@1':>6} {'Hit@3':>6} {'Hit@5':>6} {'MRR':>6}")
print(f"{'='*90}")

for p in PERMUTATIONS:
    key = (p["collection"], p["model"])
    entries = grouped[key]
    label = f"{p['collection']} + {p['model']}"
    metrics = evaluate(entries)

    if not metrics:
        print(f"{label:<40} No data found")
        continue

    for level in ["chunk_level", "article_level"]:
        m = metrics[level]
        level_label = "chunk" if level == "chunk_level" else "article"
        print(f"{label:<40} {level_label:<10} {m['hit@1']:>6.3f} {m['hit@3']:>6.3f} {m['hit@5']:>6.3f} {m['MRR']:>6.3f}")

    print(f"{'-'*90}")
    report.append({"permutation": label, **metrics})

print(f"{'='*90}\n")

with open("evaluation/report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("Full report saved to evaluation/report.json")


# This outputs a table like:
# ```
# ==========================================================================================
# Permutation                              Level      Hit@1  Hit@3  Hit@5    MRR
# ==========================================================================================
# chunks + voyage-4-large                  chunk      0.340  0.510  0.600  0.430
# chunks + voyage-4-large                  article    0.530  0.720  0.810  0.620
# ------------------------------------------------------------------------------------------
# chunks + voyage-4                        chunk      0.320  0.490  0.580  0.410
# ...