"""
This file contains method 'search' which does retrieval from mongodb based on the 
similarity score compared with the query.

The 'search' method is later given to an ai agent
"""
from pymongo import MongoClient
import voyageai
from dotenv import load_dotenv
import os

load_dotenv()

# init
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))


COLLECTIONS = {
    "chunks":    client["armenian_search"]["court_case"]
}

INDEX_NAMES = {
    "chunks":    "vector_index_court"
}

def search(query: str, k: int = 5) -> dict:
    collection = "chunks"
    model = "voyage-4-lite"
    query_embedding = vo.embed(
        texts=[query],
        model=model,
        input_type="query"
    ).embeddings[0]

    raw_results = COLLECTIONS[collection].aggregate([
        {
            "$vectorSearch": {
                "index": INDEX_NAMES[collection],
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": k * 10,
                "limit": k
            }
        },
        {
            "$project": {
                "text": 1,
                "chunkID": 1,
                "heading": 1,
                "page_number": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ])

    results = []
    for r in raw_results:
        results.append({
            "rank":    len(results) + 1,
            "text":    r["text"],
            #"article": r.get("article", ""),
            "score":   r["score"],
            "_id":     str(r["_id"]),
            #"articleID": r["articleID"],
            "chunkID": r["chunkID"],
            "page_number": r["page_number"]
        })

    return {
        #"query":           query,
        "query":           query,
        "collection":      collection,
        "embedding_model": model,
        "results":         results
    }


