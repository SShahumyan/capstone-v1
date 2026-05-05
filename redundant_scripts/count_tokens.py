import json
import tiktoken

# ---- CONFIG ----
FILE_PATH = "data/armenian_chunks.json"
TOKEN_LIMIT = 8192
SAFE_LIMIT = 8000  # slightly below max for safety

# ---- LOAD TOKENIZER ----
enc = tiktoken.get_encoding("cl100k_base")

# ---- LOAD DATA ----
with open(FILE_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks\n")

# ---- ANALYSIS ----
max_tokens = 0
max_index = -1

too_large = []

for i, item in enumerate(chunks):
    text = item["text"]

    # safety check
    if not isinstance(text, str):
        print(f"⚠️ Non-string text at index {i}: {type(text)}")
        continue

    tokens = len(enc.encode(text))

    # track max
    if tokens > max_tokens:
        max_tokens = tokens
        max_index = i

    # track problematic
    if tokens > SAFE_LIMIT:
        too_large.append((i, tokens, item.get("article", "UNKNOWN")))

# ---- RESULTS ----
print("✅ Analysis complete\n")

print(f"📊 Longest chunk:")
print(f"   Index: {max_index}")
print(f"   Tokens: {max_tokens}")
print(f"   Article: {chunks[max_index].get('article', 'UNKNOWN')}\n")

print(f"⚠️ Chunks over {SAFE_LIMIT} tokens: {len(too_large)}\n")

for i, tokens, article in too_large[:20]:  # print first 20 only
    print(f"❌ Index {i} | Tokens: {tokens} | Article: {article}")

if len(too_large) > 20:
    print(f"... and {len(too_large) - 20} more\n")

# ---- OPTIONAL: SAVE PROBLEMATIC CHUNKS ----
if too_large:
    bad_chunks = [chunks[i] for i, _, _ in too_large]

    with open("bad_chunks.json", "w", encoding="utf-8") as f:
        json.dump(bad_chunks, f, ensure_ascii=False, indent=2)

    print("💾 Saved problematic chunks to bad_chunks.json")