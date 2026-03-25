# Decisions You Have to Make

> These are the choices that will shape your project. Each one has a recommended default — take it unless you have a specific reason not to.

---

## Decision 1: Which Voyage Model to Use

**Your choice:** `voyage-multilingual-2` vs `voyage-3` vs `voyage-3-lite` (or the voyage-4 equivalent when available)

**The trade-off:**

| Model | Multilingual Quality | Speed | Cost | Dimensions |
|---|---|---|---|---|
| `voyage-multilingual-2` | Best for Armenian | Medium | Higher | 1024 |
| `voyage-3` | Good (English-dominant) | Medium | Medium | 1024 |
| `voyage-3-lite` | Lower | Fast | Cheapest | 512 |

**Recommendation:** Start with `voyage-multilingual-2`. It's the most likely to handle Armenian well. Once your pipeline works, you can swap models and compare results — that comparison is the actual experiment.

**Action needed:** Check https://docs.voyageai.com for the exact voyage-4 model names and whether a voyage-4 multilingual variant exists.

---

## Decision 2: What Armenian Text Dataset to Use

**Your choice:** Generate synthetic data vs use a public corpus

**Options ranked by ease:**

1. **Generate with Claude API** — Ask Claude to write 50–100 Armenian paragraphs on varied topics (history, food, geography, technology). Fast, controlled, no licensing issues. Good for a prototype.

2. **Armenian Wikipedia dump** — Real, diverse text. Free. Download from https://dumps.wikimedia.org/hywiki/ (Eastern Armenian) or https://dumps.wikimedia.org/hywwiki/ (Western Armenian). Requires parsing XML — more setup work.

3. **OPUS corpus** — Open multilingual parallel corpus with Armenian data. Available at https://opus.nlpl.eu — filtered/preprocessed versions exist.

4. **Your own documents** — Only if you have them.

**Recommendation for Day 1:** Use Claude to generate synthetic Armenian text. You can switch to Wikipedia later. Keep it simple while you're learning the pipeline.

**Size target:** 50–200 text chunks is enough for a meaningful test. You don't need thousands of documents to validate the approach.

---

## Decision 3: MongoDB Atlas Tier

**Your choice:** Free (M0) vs paid tier

**M0 Free tier limits:**
- 512 MB storage
- Supports Atlas Vector Search ✓
- Limited connections and IOPS
- Sufficient for a prototype with hundreds of documents

**Recommendation:** M0 is fine for this project. Don't pay for anything yet.

**Action needed:** Sign up at https://cloud.mongodb.com — takes 10 minutes. Create a cluster in a region close to Armenia (e.g., `aws-eu-west-1` in Ireland or `gcp-europe-west3` in Frankfurt).

---

## Decision 4: How to Chunk Armenian Text

**Your choice:** By paragraph, by fixed character count, or by sentence

**The trade-off:**
- **By paragraph** — Easiest to implement, natural boundaries, variable chunk size
- **By fixed character count (e.g., 500 chars, 100 overlap)** — Consistent, predictable, slightly unnatural
- **By sentence** — Best semantically, but Armenian sentence boundary detection is unreliable with simple tools

**Recommendation:** Use paragraph splitting first. If paragraphs are very long (>800 chars), split further by fixed character count.

```python
# Simple paragraph split
chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
```

---

## Decision 5: What Metadata to Store Alongside Embeddings

**Your choice:** Minimal vs rich metadata

At minimum, store:
```json
{
  "text": "the actual chunk text",
  "embedding": [...],
  "source": "wikipedia / synthetic / etc",
  "chunk_index": 0,
  "language": "hy"
}
```

Optional additions: `doc_title`, `word_count`, `created_at`

**Recommendation:** Keep it minimal. You can always add fields later. Don't let schema design slow you down on Day 1.

---

## Decision 6: How to Structure Your Evaluation

**Your choice:** Manual inspection vs automated metrics

Since this is an exploratory capstone (not a production system), you don't need formal recall/precision metrics right now.

**Recommended approach:** Design 10–15 test queries in Armenian. After building the system, run each query and manually assess whether the top-3 returned chunks are relevant. That's a valid qualitative evaluation.

Example test queries to prepare:
- Topic-overlap queries (query about X, document discusses X differently)
- Cross-register queries (formal query, informal document)
- Partial-match queries (query mentions a subtopic of the document)

---

## Summary: Recommended Defaults

| Decision | Recommended Choice |
|---|---|
| Voyage model | `voyage-multilingual-2` (swap for voyage-4 multilingual if available) |
| Dataset | Claude-generated synthetic Armenian text |
| Atlas tier | M0 (free) |
| Chunking | By paragraph, fallback to 500-char fixed chunks |
| Metadata | Minimal: text, source, chunk_index, language |
| Evaluation | 10–15 manual test queries |
