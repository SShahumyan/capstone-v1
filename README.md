# Armenian Retrieval Benchmark (ARAG)

**How well do modern embedding models actually retrieve Armenian text?**

Most embedding models are benchmarked on English. Armenian is a low-resource language with its own script, rich inflection, and almost no public retrieval benchmarks. This project builds one — two Armenian corpora, LLM-generated question sets, and a MongoDB Atlas vector-search harness — and measures six embedding models against them.

The short answer: **the gap between providers on Armenian is far larger than their published English benchmarks suggest.** On Armenian legal text, the best OpenAI model scores an MRR of 0.134 where Voyage scores 0.678 — a 5× difference on identical chunks, identical questions, identical retrieval code.

---

## Key results

Retrieval is scored with **Hit@k** (was the source chunk returned in the top *k*?) and **MRR** (mean reciprocal rank of the source chunk). Higher is better; 1.000 is perfect.

### Armenian Wikipedia — 7,324 chunks, 147 questions

| Document embeddings | Query model | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| chunks | gemini-embedding-2 | 0.891 | 0.986 | **1.000** | **0.938** |
| chunks_v4 | voyage-4 | 0.810 | 0.925 | 0.939 | 0.868 |
| chunks | voyage-4 | 0.816 | 0.898 | 0.925 | 0.860 |
| chunks | voyage-4-large | 0.810 | 0.898 | 0.918 | 0.857 |
| chunks | voyage-4-lite | 0.776 | 0.857 | 0.898 | 0.819 |
| chunks | text-embedding-3-large | 0.354 | 0.639 | 0.789 | 0.507 |
| chunks | text-embedding-3-small | 0.361 | 0.551 | 0.673 | 0.470 |

*Chunk-level scores. Because wiki chunks belong to articles, article-level scores are also reported in `metrics/` and run 3–4 points higher (e.g. `chunks_v4 + voyage-4` reaches 0.892 MRR at article level).*

### Armenian court case — 2,520 chunks from an 830-page scanned PDF, 498 questions

| Document embeddings | Query model | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| chunks | voyage-4-large | 0.584 | 0.766 | 0.831 | **0.678** |
| chunks_v4 | voyage-4 | 0.519 | 0.779 | 0.831 | 0.645 |
| chunks | voyage-4-lite | 0.545 | 0.688 | 0.818 | 0.641 |
| chunks | voyage-4 | 0.545 | 0.727 | 0.792 | 0.640 |
| chunks_v4_lite | voyage-4-lite | 0.519 | 0.753 | 0.805 | 0.637 |
| chunks_v4 | voyage-4-lite | 0.481 | 0.727 | 0.844 | 0.623 |
| chunks | text-embedding-3-large | 0.098 | 0.171 | 0.191 | 0.134 |
| chunks | text-embedding-3-small | 0.016 | 0.026 | 0.034 | 0.022 |

### What the numbers say

1. **Provider choice dominates every other variable.** Model size, chunking strategy, and query/document model pairing all move MRR by a few points. Switching provider moves it by 40–65 points. On the court case, `text-embedding-3-small` retrieves the correct chunk in the top 5 for **3% of queries** — effectively unusable for Armenian.
2. **Gemini's embedding model leads on Wikipedia** (0.938 MRR, perfect Hit@5), ahead of the best Voyage configuration by ~7 points. The original goal of this project was to evaluate the Voyage-4 series; Gemini was added as a control and won that corpus.
3. **Clean text is a much easier problem than real documents.** The same Voyage models drop from ~0.86 MRR on Wikipedia to ~0.65 on OCR'd legal text — scanned scripts, dense legal register, and near-duplicate procedural passages all cost retrieval accuracy.
4. **Cross-model retrieval works within the Voyage family.** Documents embedded with one Voyage model and queried with another perform comparably to matched pairs, which makes incremental re-embedding cheaper.

---

## How it works

```
corpus ──> chunk ──> embed ──> MongoDB Atlas ──> $vectorSearch ──> FastAPI /search ──> agent
                                (one collection +
                                 index per model)
             │
             └──> sample chunks ──> LLM question generation ──> ground truth ──> evaluation
```

**Corpora**

- *Armenian Wikipedia* — `hywiki-latest-pages-articles.xml.bz2` parsed and chunked into 7,324 passages with article attribution.
- *Court case* — an 830-page scanned Armenian PDF, split into batches and OCR'd with `gemini-3-flash-preview` using a structured-output schema (`heading`, `text`, `page_number`), producing 2,520 paragraph-level chunks across 88 batch files.

**Indexing** — each document-embedding model gets its own Atlas collection and vector index (`chunks` / `chunks_v4` / `chunks_v4_lite`, `court_case` / `court_case_v4` / `court_case_v4_lite`, plus OpenAI and Gemini variants), so permutations are directly comparable on the same underlying text. Section headings are prepended to chunk text at embedding time (`[Բաժին: {heading}] {text}`) but stored separately, which measurably improves retrieval on the structured legal document.

**Ground truth** — chunks are randomly sampled, and `gemini-3-flash-preview` is prompted **in Armenian** to write one natural question answerable from that chunk without quoting it directly. The chunk it was generated from is the single correct answer. Generation is checkpointed and resumable.

**Evaluation** — every question is run against every permutation, raw rankings are stored in `evaluation/`, and `scripts/evaluation*.py` computes Hit@1/3/5 and MRR at chunk and article level.

**Serving** — `main.py` exposes `POST /search` via FastAPI. `agent/search_agent.py` wraps the same retrieval function as a tool for an LLM agent, so the benchmark's winning configuration is directly usable as a RAG backend.

---

## Setup

Requires Python 3.11+ and a MongoDB Atlas cluster with vector search enabled.

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
MONGODB_URI=...
VOYAGE_API_KEY=...
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

Each Atlas collection needs a vector index on the `embedding` field with the matching dimension for its model, named as referenced in `scripts/search*.py` (`vector_index`, `vector_index_v4`, `vector_index_court`, …).

Run the search API:

```bash
uvicorn main:app --reload
curl -X POST localhost:8000/search -H "Content-Type: application/json" -d "{\"query\": \"...\"}"
```

Reproduce an evaluation end to end:

```bash
python scripts/ocr_pdf.py                 # scanned PDF -> structured chunks
python scripts/embed_qg.py                # chunks -> embeddings -> Atlas
python scripts/create_ground_truth_qg.py  # sample chunks -> generated questions
python scripts/generate_results_qg.py     # run every permutation, store rankings
python scripts/evaluation.py              # rankings -> Hit@k / MRR tables
```

---

## Repo layout

| Path | Contents |
|---|---|
| `main.py` | FastAPI `/search` endpoint |
| `agent/` | LLM agents using retrieval as a tool |
| `scripts/` | OCR, chunking, embedding, question generation, evaluation |
| `metrics/` | Final result tables (the numbers above) |
| `evaluation/` | Ground truth and raw per-query rankings |
| `data/`, `data_qg/` | Corpora and OCR output |
| `redundant_scripts/` | Earlier iterations, kept for reference |

---

## Limitations

Stated plainly, because they bound how far these numbers generalize:

- **Questions are LLM-generated, not human-written.** Each question is produced from the chunk that counts as its correct answer, which biases the set toward questions whose phrasing tracks that chunk. This inflates absolute scores across the board — but it does so equally for every model, so the *relative* comparison is the trustworthy part.
- **The wiki set is small** at 147 questions; differences of 1–2 points between adjacent configurations are within noise. The 498-question court set is more reliable.
- **OCR is imperfect.** Gemini occasionally confuses visually similar Armenian characters (ղ/դ, գ/զ) in proper names, so a fraction of chunks contain corrupted entities. This penalizes all models equally but does add floor noise.
- **One document, one domain** on the harder corpus. Armenian legal prose is not representative of Armenian text generally.
- **Retrieval only.** This measures whether the right passage is found, not whether an LLM then produces a correct answer from it.
- **Costs are not modeled.** `voyage-4-lite` and `gemini-embedding-2` differ substantially in price per token; the tables rank accuracy alone.

---

## Write-up

- `Capstone_paper_Samvel_Shahumyan.pdf` — full paper
- `Samvel_Shahumyan_ARAG_Project_Brief.pdf` — project brief
- `arag_presentation_pdf.pdf` — presentation

**Stack:** Python · MongoDB Atlas Vector Search · FastAPI · Voyage AI · Google Gemini · OpenAI
