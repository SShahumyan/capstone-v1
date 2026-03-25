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
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ])

    return list(results)

print(search("ինչպե՞ս"))