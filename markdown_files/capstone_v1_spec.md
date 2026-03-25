# capstone-v1
## Armenian NLP + Semantic Vector Search — Project Specification

> **Version:** 1.0 | **Status:** In development | **Timeline:** 3 days | **Type:** Research prototype

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Dataset](#4-dataset)
5. [Key Design Decisions](#5-key-design-decisions)
6. [Project File Structure](#6-project-file-structure)
7. [Three-Day Execution Plan](#7-three-day-execution-plan)
8. [Risk Register](#8-risk-register)
9. [Evaluation Plan](#9-evaluation-plan)
10. [Future Work](#10-future-work)
11. [Glossary](#glossary)

---

## 1. Project Overview

capstone-v1 is a self-contained research and engineering project to evaluate Voyage AI's voyage-4 series embedding models on Armenian-language text. The project builds a full semantic search pipeline: text is chunked, embedded using Voyage AI, stored in MongoDB Atlas, and retrieved via vector similarity queries.

**Primary research question:** How well do Voyage AI's multilingual embedding models represent Armenian text in semantic vector space, and can they power meaningful similarity-based retrieval on that language?

### 1.1 Objectives

- Set up a cloud-hosted vector database using MongoDB Atlas with vector search indexing
- Source or generate an Armenian-language text dataset (50–200 chunks)
- Embed all text chunks using Voyage AI voyage-4 series models and store them in Atlas
- Implement semantic query support: embed a query, retrieve the top-k most similar chunks
- Evaluate retrieval quality manually using 10–15 designed test queries
- Document findings on how well Voyage AI handles Armenian

### 1.2 What This Project Is Not

- Not a production system — no authentication, rate limiting, or scaling concerns
- Not a RAG pipeline — retrieval only, no generation step
- Not a fine-tuning project — models are used off-the-shelf
- Not a benchmarking study — evaluation is qualitative and exploratory

---

## 2. Technology Stack

### 2.1 Core Technologies

| Component | Role | Details |
|---|---|---|
| Voyage AI | Embedding models | `voyage-multilingual-2` / voyage-4 series — converts Armenian text into dense vectors |
| MongoDB Atlas | Cloud database + vector store | M0 free tier — stores documents and embeddings; Atlas Vector Search handles ANN queries |
| Python 3.11+ | Application language | Scripts for data generation, embedding pipeline, batch ingestion, and query interface |
| `voyageai` | Voyage SDK | Official Python SDK for calling the Voyage embedding API |
| `pymongo` | MongoDB driver | Official Python client for connecting to and querying Atlas |
| `python-dotenv` | Config management | Loads API keys and connection strings from a `.env` file |
| `tqdm` | Progress display | Progress bars during batch embedding runs |

### 2.2 Infrastructure

- **MongoDB Atlas cluster:** M0 free tier, region `aws-eu-west-1` (Ireland) or `gcp-europe-west3` (Frankfurt)
- **Voyage AI API:** authenticated via API key stored in `.env` — never committed to version control
- **All code runs locally** — no server, no deployment, no Docker required for this prototype

---

## 3. System Architecture

### 3.1 Pipeline Overview

The system consists of two phases: an offline ingestion pipeline that runs once to populate the database, and an online query pipeline that runs interactively.

**Ingestion pipeline (offline):**
```
Armenian Text  →  Chunking  →  Voyage Embed API  →  MongoDB Atlas (text + vector stored)
```

**Query pipeline (online):**
```
User Query (Armenian)  →  Voyage Embed API  →  $vectorSearch  →  Top-k chunks returned
```

### 3.2 Data Model

Each document stored in MongoDB represents one text chunk:

```json
{
  "_id":         "ObjectId",
  "text":        "string — original Armenian text chunk",
  "embedding":   "float[1024] — voyage-multilingual-2 vector",
  "source":      "string — synthetic | wikipedia | opus",
  "chunk_index": "int — position in original document",
  "language":    "hy",
  "created_at":  "ISODate — optional"
}
```

### 3.3 Vector Search Index

Created in the MongoDB Atlas UI on the `chunks` collection:

```json
{
  "fields": [
    {
      "type":          "vector",
      "path":          "embedding",
      "numDimensions": 1024,
      "similarity":    "cosine"
    }
  ]
}
```

Cosine similarity is used because it measures the angle between vectors (semantic direction) rather than magnitude — the standard metric for text embedding retrieval.

---

## 4. Dataset

### 4.1 Strategy

The project supports multiple dataset sources, ranked by ease of setup. The recommended starting point is synthetic data generated via the Claude API.

| Priority | Source | Notes |
|---|---|---|
| 1 — Recommended | Synthetic (Claude API) | Ask Claude to generate 50–100 Armenian paragraphs across varied topics. Fast, no licensing issues, fully controlled. |
| 2 | Armenian Wikipedia | `dumps.wikimedia.org/hywiki` — Eastern Armenian. Requires XML parsing with `wikiextractor`. |
| 3 | OPUS Corpus | `opus.nlpl.eu` has Armenian parallel data. Good for cross-lingual tests. |
| 4 | Own documents | Any Armenian-language PDFs, articles, or notes the user has access to. |

### 4.2 Target Topics (Synthetic Dataset)

Generated text should cover a range of semantic domains to make retrieval tests meaningful:

- **Armenian geography** — cities, rivers (Araks, Hrazdan), Lake Sevan, Mount Ararat
- **Armenian history** — Urartu, medieval kingdoms, Genocide, Soviet era, independence 1991
- **Armenian culture** — cuisine (khorovats, dolma, lavash), music, dance, duduk
- **Armenian language** — alphabet (Mesrop Mashtots, 405 AD), Eastern vs Western dialects
- **Modern Armenia** — economy, tech sector, diaspora communities, Yerevan city life

### 4.3 Chunking Strategy

```python
# Primary: split on double newlines (paragraph boundaries)
chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]

# Fallback: if a paragraph exceeds 800 chars, split further
CHUNK_SIZE = 500   # characters
OVERLAP    = 100   # characters of overlap between adjacent chunks
```

Target chunk size: 200–500 characters (~50–150 Armenian words). Overlap ensures context is not lost at chunk boundaries.

---

## 5. Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Voyage model | `voyage-multilingual-2` | Best multilingual coverage. Swap for voyage-4 multilingual when available. Use `voyage-3` as comparison baseline. |
| `input_type` param | `document` / `query` | Pass `"document"` when embedding stored chunks, `"query"` for user queries. Improves retrieval quality. |
| Vector dimensions | 1024 | Fixed by `voyage-multilingual-2`. Must match `numDimensions` in the Atlas index. |
| Similarity metric | cosine | Standard for text embeddings. Measures semantic direction, not magnitude. |
| Atlas tier | M0 free | Sufficient for a prototype with hundreds of documents. No cost. |
| Batch size | 8 chunks/call | Conservative default to avoid Voyage API rate limits. Increase to 32 once stable. |
| Evaluation method | Manual (qualitative) | 10–15 test queries judged as Relevant / Partial / Not Relevant. No automated metrics for v1. |
| `numCandidates` | `top_k * 10` | Atlas pre-filters this many candidates before returning top_k. Standard heuristic. |

---

## 6. Project File Structure

```
armenian-vector-search/
├── .env                      # API keys — never commit
├── .gitignore                # must include .env and data/
├── README.md                 # setup + usage + findings
├── requirements.txt          # voyageai, pymongo, python-dotenv, tqdm
│
├── data/
│   ├── armenian_texts.txt    # raw text, one paragraph per line
│   └── chunks.json           # optional: cached chunks before embedding
│
├── scripts/
│   ├── 01_test_embedding.py  # sanity check: embed one string
│   ├── 02_test_mongodb.py    # sanity check: insert and retrieve one doc
│   ├── 03_generate_data.py   # generate synthetic Armenian text
│   ├── 04_embed_and_store.py # full ingestion pipeline
│   └── 05_test_search.py     # one-shot query test
│
├── search.py                 # ArmenianVectorSearch class (reusable module)
├── cli.py                    # interactive query CLI
│
└── evaluation/
    ├── test_queries.txt      # 10–15 Armenian test queries
    └── results.md            # manual evaluation results
```

---

## 7. Three-Day Execution Plan

### Day 1 — Infrastructure & First Embedding
**Goal:** one Armenian sentence embedded and stored in MongoDB Atlas.

| Session | Tasks |
|---|---|
| Morning (~1.5 hrs) | Create MongoDB Atlas account → free M0 cluster → database user → IP whitelist → copy connection string |
| Afternoon (~1.5 hrs) | Set up Python venv → install dependencies → write `01_test_embedding.py` → confirm 1024-dim vector prints |
| Evening (~1 hr) | Write `02_test_mongodb.py` → embed one sentence → insert document → confirm in Atlas UI |
| **Day 1 done** | Full pipeline plumbing works end-to-end with a single document |

### Day 2 — Dataset, Batch Embedding & Vector Index
**Goal:** 50+ chunks stored, vector index live, first real search results returning.

| Session | Tasks |
|---|---|
| Morning (~1.5 hrs) | Generate Armenian text dataset — 50+ paragraphs across 5 topic areas — save to `data/armenian_texts.txt` |
| Afternoon (~2 hrs) | Write `04_embed_and_store.py` — batch embed all chunks — insert into Atlas — verify document count |
| Evening (~1 hr) | Create vector search index in Atlas UI → wait for Active status → run `05_test_search.py` → inspect results |
| **Day 2 done** | Semantic search working — queries return ranked Armenian chunks |

### Day 3 — Query Interface, Evaluation & Documentation
**Goal:** clean search tool, written evaluation, finished README.

| Session | Tasks |
|---|---|
| Morning (~1.5 hrs) | Refactor into `search.py` module (`ArmenianVectorSearch` class) + `cli.py` interactive query loop |
| Afternoon (~2 hrs) | Run 10–15 test queries — record scores and text previews — judge relevance — write `evaluation/results.md` |
| Evening (~1 hr) | Write `README.md` — setup steps, usage, findings — commit to git (without `.env`) |
| **Day 3 done** | Complete, demonstrable capstone project with documented results |

---

## 8. Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Atlas connection refused | Medium | IP not whitelisted. Fix: Network Access → Add `0.0.0.0/0` temporarily during development. |
| Voyage rate limits | Medium | Too many requests. Fix: batch size of 8, add `time.sleep(0.5)` between batches. |
| Armenian encoding errors | Low | File not read as UTF-8. Fix: always open files with `encoding='utf-8'`. |
| Vector index dimension mismatch | Low | `numDimensions` in index doesn't match model output. Fix: confirm model dims before creating index. |
| Insufficient Armenian text | Low | Not enough diverse content for meaningful retrieval tests. Fix: generate more with Claude API. |
| Poor retrieval quality | Expected | Armenian is lower-resource in training data. Document this as a finding, not a failure. |

---

## 9. Evaluation Plan

### 9.1 Test Query Design

15 test queries are prepared in Armenian before running the evaluation, covering:

- **Topic overlap** — query discusses X, target document discusses X from a different angle
- **Cross-register** — formal query against informal document text (or vice versa)
- **Partial-match** — query mentions a subtopic of a broader document
- **Cross-lingual** — English or Russian query, Armenian target (tests multilingual alignment)
- **Near-miss** — semantically adjacent but not quite matching topics

### 9.2 Relevance Judgments

Each top-3 result is manually judged on a 3-point scale:

| Label | Definition |
|---|---|
| Relevant | The returned chunk is clearly about the same topic as the query. A user would find it useful. |
| Partially Relevant | The returned chunk shares some context with the query but doesn't directly address it. |
| Not Relevant | The returned chunk has no meaningful connection to the query topic. |

### 9.3 Success Criteria

- Top-1 result is Relevant for at least 8 of 15 queries
- At least one Relevant result in top-3 for at least 12 of 15 queries
- Cross-lingual queries (English/Russian → Armenian) return at least partially relevant results

If results are poor, the finding itself is valuable — it documents the limitations of current multilingual models on Armenian.

---

## 10. Future Work

- **Model comparison** — run same queries against `voyage-3`, `voyage-3-lite`, and `voyage-multilingual-2`; compare precision
- **Reranking** — add a Voyage reranking model pass after initial retrieval to improve top-k quality
- **Larger dataset** — replace synthetic data with Armenian Wikipedia or OPUS corpus
- **RAG pipeline** — add a generation step: use retrieved chunks as context for a Claude answer
- **Western Armenian** — test on Western Armenian dialect text (different from Eastern Armenian used in Republic of Armenia)
- **Metadata filtering** — add Atlas Search prefilters (e.g., filter by source or topic before vector search)
- **Web UI** — wrap the CLI in a simple FastAPI + HTML frontend

---

## Glossary

| Term | Definition |
|---|---|
| Embedding | A fixed-length array of floats that encodes the meaning of a text string, produced by an embedding model. |
| Vector search | Finding stored vectors that are numerically closest to a query vector, interpreted as semantic similarity. |
| Cosine similarity | A distance metric measuring the angle between two vectors. 1.0 = identical direction; 0 = orthogonal. |
| Chunking | Splitting long documents into smaller pieces before embedding, since models have input length limits. |
| ANN | Approximate Nearest Neighbor — fast algorithm used by Atlas Vector Search to find close vectors at scale. |
| `$vectorSearch` | MongoDB aggregation pipeline stage that performs ANN search on a vector-indexed field. |
| `numCandidates` | In `$vectorSearch`: how many candidates Atlas pre-selects before returning the final `top_k` results. |
| `input_type` | Voyage API parameter — `"document"` for stored text, `"query"` for search queries. |
| M0 | MongoDB Atlas free tier — 512 MB storage, shared compute, sufficient for prototypes. |
| `hy` | ISO 639-1 language code for Armenian (Հայերեն). |
