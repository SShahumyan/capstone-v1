"""
This file contains method 'search' which does retrieval from mongodb based on the 
similarity score compared with the query.

The 'search' method is later handeled by main.py which handeles post request
"""
from pymongo import MongoClient
import voyageai
from dotenv import load_dotenv
import os

load_dotenv()

# init
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
#collection = client["armenian_search"]["chunks"]

COLLECTIONS = {
    "chunks":    client["armenian_search"]["court_case"],
    "chunks_v4": client["armenian_search"]["court_case_v4"],
    "chunks_v4_lite": client["armenian_search"]["court_case_v4_lite"],
}

INDEX_NAMES = {
    "chunks":    "vector_index_court",
    "chunks_v4": "vector_index_court_v4",
    "chunks_v4_lite": "vector_index_court_v4_lite",
}

"""
This file contains method 'search' which does retrieval from mongodb based on the 
similarity score compared with the query.

The 'search' method is later handeled by main.py which handeles post request
"""
# from pymongo import MongoClient
# import voyageai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # init
# vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
# client = MongoClient(os.getenv("MONGODB_URI"))
# #collection = client["armenian_search"]["chunks"]

# COLLECTIONS = {
#     "chunks":    client["armenian_search"]["chunks"],
#     "chunks_v4": client["armenian_search"]["chunks_v4"],
#     "chunks_v4_lite": client["armenian_search"]["chunks_v4_lite"],
# }

# INDEX_NAMES = {
#     "chunks":    "vector_index",
#     "chunks_v4": "vector_index_v4",
#     "chunks_v4_lite": "vector_index_v4_lite",
# }

def search(query: str, collection: str = "chunks", model: str = "voyage-4-large", k: int = 5) -> dict:
    query_embedding = vo.embed(
        texts=[query[:len(query)//2]],
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
            #"text":    r["text"],
            #"article": r.get("article", ""),
            "score":   r["score"],
            "_id":     str(r["_id"]),
            #"articleID": r["articleID"],
            "chunkID": r["chunkID"],
            "page_number": r["page_number"]
        })

    return {
        "query":           query,
        "collection":      collection,
        "embedding_model": model,
        "results":         results
    }


