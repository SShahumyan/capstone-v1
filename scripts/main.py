from fastapi import FastAPI
from pydantic import BaseModel
#from 05_retrieval_test import search  # 👈 import your function
from retrieval import search

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/search/v4large")
def search_endpoint(q: Query):
    if not q.query or len(q.query) < 2:
        return {"error": "Query too short"}

    results = search(q.query, "voyage-4-large")

    # convert ObjectId → string
    for r in results:
        r["_id"] = str(r["_id"])

    return results


@app.post("/search/v4")
def search_endpoint(q: Query):
    if not q.query or len(q.query) < 2:
        return {"error": "Query too short"}

    results = search(q.query, "voyage-4")

    # convert ObjectId → string
    for r in results:
        r["_id"] = str(r["_id"])

    return results

@app.post("/search/v4lite")
def search_endpoint(q: Query):
    if not q.query or len(q.query) < 2:
        return {"error": "Query too short"}

    results = search(q.query, "voyage-4-lite")

    # convert ObjectId → string
    for r in results:
        r["_id"] = str(r["_id"])

    return results