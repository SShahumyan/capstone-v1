# Concepts to Learn: Armenian NLP + Vector Search Capstone

> You're a beginner to most of these technologies. This doc covers what you **actually need to understand** — not everything that exists, just what's relevant to your project.

---

## 1. Embeddings — The Core Idea

**What they are:** Embeddings convert text into arrays of numbers (vectors) that capture *meaning*. Similar sentences end up with vectors that are numerically "close" to each other.

**Why it matters for your project:** Instead of searching for exact words, you'll search by *meaning*. A query like "Երևան բնակչություն" (Yerevan population) can match a document that talks about "հայաստանի մայրաքաղաք" (Armenia's capital) — because the meanings are related.

**What you need to know:**
- A model like `voyage-multilingual-2` takes a string → returns a list of floats (e.g., 1024 floats)
- These are stored in a database with the original text
- At query time, your query is also embedded, then you find stored vectors that are "close"
- "Closeness" is measured with **cosine similarity** (angle between vectors) — you don't need to implement this, MongoDB does it

**Key term:** `voyage-multilingual-2` or `voyage-3` — these are Voyage AI's models that support non-English languages including Armenian.

---

## 2. Voyage AI Models (voyage-4 series)

**What they are:** Voyage AI is an embeddings-focused company. Their models turn text into vectors.

**What you need to know:**
- Models: `voyage-3`, `voyage-3-lite`, `voyage-multilingual-2` — check their docs for the latest voyage-4 series names
- You call their API with a list of strings → get back a list of vectors
- Input limit per call: ~8,000–16,000 tokens depending on model
- `input_type` parameter: use `"document"` when embedding stored text, `"query"` when embedding a search query (this improves retrieval quality)
- **Cost:** you're billed per token embedded — multilingual models tend to cost more

**Armenian language note:** Voyage's multilingual models are trained on many languages. Armenian (both Eastern and Western) has limited representation in most training corpora, so results may be imperfect — that's partly what you're testing.

---

## 3. Text Chunking

**What it is:** Before embedding, you split documents into smaller pieces ("chunks"). You can't embed a 10-page article as one vector effectively.

**What you need to know:**
- Chunk size: typically 200–500 tokens (roughly 150–400 words)
- Overlap: chunks can overlap slightly (e.g., 50 tokens) so context isn't lost at boundaries
- Armenian text chunking: splitting on sentences or paragraphs works well; word-level tokenization is trickier because Armenian morphology is complex
- Simple approach: split by paragraph or by fixed character count (e.g., 500 chars with 100-char overlap)

---

## 4. MongoDB Atlas + Vector Search

**What MongoDB Atlas is:** A cloud-hosted MongoDB database. MongoDB stores documents as JSON-like objects (called BSON).

**What Vector Search adds:** A special index type (`vectorSearch`) that lets you do nearest-neighbor queries on stored vectors — very fast even at large scale.

**What you need to know:**
- You store documents like: `{ text: "...", embedding: [...], metadata: {...} }`
- You create a **vector search index** on the `embedding` field specifying dimensions (e.g., 1024) and similarity metric (`cosine`)
- Query syntax uses the `$vectorSearch` aggregation stage (MongoDB's special syntax)
- Free tier (M0) supports vector search with limits — sufficient for a prototype
- Atlas has a web UI — you'll configure the index there, not in code

**Key mental model:** MongoDB = your storage. Atlas Vector Search = your search engine on top of it.

---

## 5. The Pipeline End-to-End

```
Armenian Text
     ↓
  Chunking  (split into ~300-token pieces)
     ↓
  Voyage API  (embed each chunk → vector)
     ↓
  MongoDB Atlas  (store text + vector + metadata)
     ↓
  User Query  (embed query → vector)
     ↓
  $vectorSearch  (find top-k nearest vectors)
     ↓
  Return matching text chunks
```

Understanding this flow is more important than any individual technology.

---

## 6. Python Libraries You'll Use

| Library | Purpose |
|---|---|
| `voyageai` | Official Voyage AI Python SDK |
| `pymongo` | Connect to and query MongoDB from Python |
| `python-dotenv` | Load API keys from a `.env` file safely |
| `tqdm` | Progress bars (helpful when embedding many chunks) |
| `tiktoken` or `langdetect` | Optional: count tokens or detect language |

You don't need LangChain or any heavy framework for this project.

---

## 7. What You Don't Need to Learn (Yet)

- Fine-tuning embedding models
- FAISS or other local vector DBs (you're using Atlas)
- LangChain / LlamaIndex
- Reranking models
- RAG (Retrieval Augmented Generation) — you're doing retrieval only, not generation

---

## Suggested Learning Order

1. Read Voyage AI quickstart docs — make one API call, print the vector
2. Create a free MongoDB Atlas cluster, insert one document via Python
3. Watch one short YouTube video on "what are embeddings" (3Blue1Brown or similar)
4. Understand the `$vectorSearch` aggregation stage from MongoDB docs
5. Then start building
