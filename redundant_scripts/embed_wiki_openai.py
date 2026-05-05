"""
this is a code responsible for adding vectors to mongodb.
It adds contents from data/armenian_chunks.json currently.
"""
#import voyageai
from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv
from tqdm import tqdm
import time
from openai import OpenAI
from google import genai
from google.genai import types


load_dotenv()

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["armenian_search"]["chunks"]

# Clear previous data
collection.delete_many({})
print("Cleared old documents")

with open("data/armenian_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

BATCH_SIZE = 8
docs_to_insert = []

for i in tqdm(range(0, len(chunks), BATCH_SIZE)):
    batch = chunks[i:i + BATCH_SIZE]
    texts = [item["text"] for item in batch]

    #result = vo.embed(texts, model="voyage-4-lite", input_type="document")
    for idx, t in enumerate(texts):
        if len(t) > 20000:  # char-based quick check
         print(f"⚠️ Large chunk at batch index {i}, item {idx}, length={len(t)}")

    response_large = openai_client.embeddings.create(
        model="text-embedding-3-large",  # or "text-embedding-3-small"
        input=texts
    )

    response_small = openai_client.embeddings.create(
        model="text-embedding-3-small",  # or "text-embedding-3-small"
        input=texts
    )

    # response_gemini = gemini_client.models.embed_content(
    # model="gemini-embedding-2",
    # contents=texts,
    # config=types.EmbedContentConfig(
    #     task_type="RETRIEVAL_DOCUMENT", # Equivalent to Voyage's "document"
    #     output_dimensionality=3072      # Gemini 2 default (supports 128 to 3072)
    #     )
    # )

    embeddings_large = [item.embedding for item in response_large.data]
    embeddings_small = [item.embedding for item in response_small.data]
   # embeddings_gemini = [item.values for item in response_gemini.embeddings]

    for j, (item, vector_large, vector_small) in enumerate(zip(batch, embeddings_large, embeddings_small)):
        docs_to_insert.append({
            "text":        item["text"],
            "embedding_large":   vector_large,
            "embedding_small": vector_small,
            #"embedding_gemini": vector_gemini,
            "article":     item["article"],
            "chunk_index": i + j,
            "source":      "wikipedia",
            "language":    "hy"
        })

    # Insert in batches of 200 to avoid memory buildup
    if len(docs_to_insert) >= 200:
        collection.insert_many(docs_to_insert)
        docs_to_insert = []

    time.sleep(0.3)

# Insert any remaining
if docs_to_insert:
    collection.insert_many(docs_to_insert)

print(f"Done — {collection.count_documents({})} documents in Atlas")