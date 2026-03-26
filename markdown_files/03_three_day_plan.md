# 3-Day Plan: Armenian Vector Search Capstone

> You're a beginner, so this plan is deliberately paced. Each day has a clear goal and ends with something working. Never skip ahead — each day builds on the last.

---

## Guiding Principles

- **One new concept at a time.** Don't set up MongoDB and learn Voyage on the same session.
- **Always have a working state.** End each session with runnable code, even if it's simple.
- **Prototype first, clean up later.** A messy script that works beats clean code that doesn't.
- **Budget ~3–5 hours/day.** Each day is designed to fit that range.

---

## Day 1 — Infrastructure & First Embedding

**Goal by end of day:** You can embed one Armenian sentence with Voyage AI and store it in MongoDB Atlas.

### Morning (~1.5 hrs): Set Up Accounts & Environment

- [ ] Create MongoDB Atlas account → https://cloud.mongodb.com
  - Create a free M0 cluster
  - Choose a region close to you (e.g., AWS `eu-west-1` Ireland)
  - Create a database user (username + password — save these)
  - Whitelist your IP address (Network Access tab → Add IP → "Allow from anywhere" for now)
  - Get your connection string: looks like `mongodb+srv://user:pass@cluster.mongodb.net/`

- [ ] Set up your Python environment
  ```bash
  mkdir armenian-vector-search
  cd armenian-vector-search
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install voyageai pymongo python-dotenv tqdm
  ```

- [ ] Create a `.env` file (never commit this to git)
  ```
  VOYAGE_API_KEY=your_key_here
  MONGODB_URI=your_connection_string_here
  ```

### Afternoon (~1.5 hrs): First Voyage API Call

Write `01_test_embedding.py`:

```python
import voyageai
from dotenv import load_dotenv
import os

load_dotenv()
client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

text = "Հայաստանը Կովկասում գտնվող երկիր է։"  # "Armenia is a country in the Caucasus"

result = client.embed([text], model="voyage-multilingual-2", input_type="document")
vector = result.embeddings[0]

print(f"Vector dimensions: {len(vector)}")
print(f"First 5 values: {vector[:5]}")
```

- [ ] Run it. If you get a 1024-dimension vector printed, Day 1 morning is done.

### Evening (~1 hr): First MongoDB Insert

Write `02_test_mongodb.py`:

```python
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import voyageai

load_dotenv()
voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
mongo = MongoClient(os.getenv("MONGODB_URI"))

db = mongo["armenian_search"]
collection = db["chunks"]

text = "Հայաստանը Կովկասում գտնվող երկիր է։"
result = voyage.embed([text], model="voyage-multilingual-2", input_type="document")
vector = result.embeddings[0]

doc = {
    "text": text,
    "embedding": vector,
    "source": "test",
    "language": "hy"
}

inserted = collection.insert_one(doc)
print(f"Inserted document ID: {inserted.inserted_id}")

# Read it back
found = collection.find_one({"_id": inserted.inserted_id})
print(f"Retrieved: {found['text']}")
```

- [ ] Run it. Go to MongoDB Atlas UI → Browse Collections → confirm the document is there.

Learn Vercel

**Day 1 done ✓** — You have the full pipeline plumbing working.

---

## Day 2 — Dataset, Batch Embedding, and Vector Index

**Goal by end of day:** 50+ Armenian text chunks embedded and stored, with a vector search index live and returning results.

### Morning (~1.5 hrs): Build Your Armenian Dataset

Option A (recommended): Generate synthetic data

Create `03_generate_dataset.py` — call Claude API or write Armenian text manually across these topics:
- Armenian geography (cities, rivers, mountains)
- Armenian history (ancient kingdoms, Soviet era, independence)
- Armenian food and culture
- Armenian language and literature
- Modern Armenia (economy, technology, diaspora)

Aim for 20–30 paragraphs per topic area, each 3–6 sentences long. Save to `data/armenian_texts.txt` — one paragraph per line.

Option B: Download Armenian Wikipedia
```bash
# Download: https://dumps.wikimedia.org/hywiki/latest/hywiki-latest-articles.xml.bz2
# Then use wikiextractor to parse it:
pip install wikiextractor
python -m wikiextractor hywiki-latest-articles.xml.bz2 -o data/wiki --no-templates
```
Then read extracted files and collect clean paragraphs.

### Afternoon (~2 hrs): Batch Embedding Script

Write `04_embed_and_store.py`:

```python
from pymongo import MongoClient
import voyageai
from dotenv import load_dotenv
import os
from tqdm import tqdm

load_dotenv()
voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
mongo = MongoClient(os.getenv("MONGODB_URI"))
collection = mongo["armenian_search"]["chunks"]

# Load your text file
with open("data/armenian_texts.txt", "r", encoding="utf-8") as f:
    raw_chunks = [line.strip() for line in f if len(line.strip()) > 50]

print(f"Loaded {len(raw_chunks)} chunks")

# Embed in batches of 8 (Voyage rate limits)
BATCH_SIZE = 8
docs_to_insert = []

for i in tqdm(range(0, len(raw_chunks), BATCH_SIZE)):
    batch = raw_chunks[i:i+BATCH_SIZE]
    result = voyage.embed(batch, model="voyage-multilingual-2", input_type="document")
    
    for j, (text, vector) in enumerate(zip(batch, result.embeddings)):
        docs_to_insert.append({
            "text": text,
            "embedding": vector,
            "chunk_index": i + j,
            "source": "synthetic",
            "language": "hy"
        })

collection.insert_many(docs_to_insert)
print(f"Inserted {len(docs_to_insert)} documents")
```

- [ ] Run it. Verify count in Atlas UI: Collections → chunks → count of documents.

### Evening (~1 hr): Create the Vector Search Index

This is done in the MongoDB Atlas UI (not in code):

1. Go to your cluster → **Search** tab (or **Atlas Search** in the sidebar)
2. Click **Create Search Index** → choose **Atlas Vector Search** (JSON editor)
3. Select database `armenian_search`, collection `chunks`
4. Paste this index definition:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    }
  ]
}
```

5. Save. Wait ~2–5 minutes for the index to build (status will show "Active").

- [ ] Confirm the index is Active in the Atlas UI.

Write a quick test query `05_test_search.py`:

```python
from pymongo import MongoClient
import voyageai
from dotenv import load_dotenv
import os

load_dotenv()
voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
mongo = MongoClient(os.getenv("MONGODB_URI"))
collection = mongo["armenian_search"]["chunks"]

query = "Հայաստանի մայրաքաղաքը"  # "The capital of Armenia"
result = voyage.embed([query], model="voyage-multilingual-2", input_type="query")
query_vector = result.embeddings[0]

results = collection.aggregate([
    {
        "$vectorSearch": {
            "index": "default",
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 50,
            "limit": 3
        }
    },
    {
        "$project": {
            "text": 1,
            "score": {"$meta": "vectorSearchScore"},
            "_id": 0
        }
    }
])

for r in results:
    print(f"Score: {r['score']:.4f}")
    print(f"Text: {r['text'][:200]}")
    print("---")
```

- [ ] Run it. You should get back relevant Armenian chunks. **Day 2 done ✓**

---

## Day 3 — Query Interface, Evaluation & Wrap-Up

**Goal by end of day:** A clean, interactive query tool and documented evaluation results.

### Morning (~1.5 hrs): Clean Up Into a Reusable Module

Refactor your scripts into a clean `search.py` module:

```python
# search.py
import voyageai
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class ArmenianVectorSearch:
    def __init__(self, model="voyage-multilingual-2"):
        self.voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.collection = MongoClient(os.getenv("MONGODB_URI"))["armenian_search"]["chunks"]
        self.model = model
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        result = self.voyage.embed([query], model=self.model, input_type="query")
        query_vector = result.embeddings[0]
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": top_k * 10,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "text": 1,
                    "source": 1,
                    "score": {"$meta": "vectorSearchScore"},
                    "_id": 0
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))
```

Then write a simple interactive CLI:

```python
# cli.py
from search import ArmenianVectorSearch

searcher = ArmenianVectorSearch()
print("Armenian Vector Search — type a query (or 'quit' to exit)\n")

while True:
    query = input("Query: ").strip()
    if query.lower() == "quit":
        break
    results = searcher.search(query, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] Score: {r['score']:.4f}")
        print(r['text'][:300])
    print("\n" + "="*50 + "\n")
```

### Afternoon (~2 hrs): Run Your Evaluation

Create `evaluation/test_queries.txt` with 10–15 Armenian queries:

```
Երևանը ո՞ր երկրի մայրաքաղաքն է
Հայկական ավանդական ուտեստներ
Արարատ լեռը
Հայ ժողովրդի պատմությունը
...
```

For each query, record the top-3 results and judge: **Relevant / Partially Relevant / Not Relevant**

Write results to `evaluation/results.md`:

```markdown
## Query: Երևանը ո՞ր երկրի մայրաքաղաքն է

| Rank | Score | Text Preview | Judgment |
|---|---|---|---|
| 1 | 0.89 | Երևանը Հայաստանի... | Relevant |
| 2 | 0.81 | ... | Relevant |
| 3 | 0.74 | ... | Partial |
```

Also test: **what happens with a Russian or English query?** Does it still return Armenian results? This tests the multilingual alignment of the embeddings.

### Evening (~1 hr): Write Your README

Write `README.md` documenting:
- What the project does
- How to set it up (`.env` vars, Atlas setup steps)
- How to run the embedding pipeline
- How to run queries
- Your evaluation findings (2–3 paragraphs on what worked, what didn't, observations about Armenian language quality)

**Day 3 done ✓ — Project complete.**

---

## Risk Register (Things That Can Slow You Down)

| Risk | Mitigation |
|---|---|
| MongoDB Atlas IP whitelist blocking connections | Allow all IPs (0.0.0.0/0) temporarily during development |
| Voyage API rate limits (slow batch embedding) | Use `time.sleep(0.5)` between batches, use batch size of 8 |
| Armenian text encoding issues | Always open files with `encoding="utf-8"` |
| Vector search index not working | Double-check `numDimensions` matches your model (1024 for multilingual-2) |
| Not enough Armenian text | Generate more with Claude — it speaks Armenian well |

---

## What "Done" Looks Like

By the end of Day 3 you will have:
- A MongoDB Atlas cluster with 50+ Armenian text chunks stored
- Each chunk embedded with a voyage-multilingual-2 vector
- A vector search index that returns semantically relevant results
- A working CLI search tool
- A written evaluation of 10–15 test queries
- A README that documents the whole thing

That's a complete, demonstrable capstone project.
