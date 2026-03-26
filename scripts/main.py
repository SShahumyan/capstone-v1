from fastapi import FastAPI
from pydantic import BaseModel
#from 05_retrieval_test import search  # 👈 import your function
from scripts.retrieval import search

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/search")
def search_endpoint(q: Query):
    if not q.query or len(q.query) < 2:
        return {"error": "Query too short"}

    results = search(q.query)

    # convert ObjectId → string
    for r in results:
        r["_id"] = str(r["_id"])

    return results
