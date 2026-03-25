import voyageai
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))

db = client["armenian_search"]
collection = db["chunks"]

text = "Հայաստանը Կովկասում գտնվող երկիր է։"

result = vo.embed([text], model="voyage-4-large")
vector = result.embeddings[0]

doc = {
    "text": text,
    "embedding": vector,
    "source": "test",
    "language": "hy"
}

inserted = collection.insert_one(doc)
print(f"Inserted ID: {inserted.inserted_id}")

found = collection.find_one({"_id": inserted.inserted_id})
print(f"Retrieved: {found['text']}")