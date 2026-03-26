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
collection = client["armenian_search"]["chunks"]



def search(query, k=5):
    # 1. embed query
    query_embedding = vo.embed(
        texts=[query],
        model="voyage-4-large"
    ).embeddings[0]

    # 2. vector search
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": k
            }
        },
        {
            "$project": {
                "text": 1,
                "article": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ])

    return list(results)

# print(search("ինչպե՞ս"))