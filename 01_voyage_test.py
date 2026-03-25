import voyageai
import os
from dotenv import load_dotenv

load_dotenv()
voyage_api_key = os.getenv("VOYAGE_API_KEY")

vo = voyageai.Client(api_key=voyage_api_key)
# This will automatically use the environment variable VOYAGE_API_KEY.
# Alternatively, you can use vo = voyageai.Client(api_key="<your secret key>")

text = "Հայաստանը Կովկասում գտնվող երկիր է։"  # "Armenia is a country in the Caucasus"

result = vo.embed([text], model="voyage-4-large")
vector = result.embeddings[0]

print(f"Dimensions: {len(vector)}")
print(f"First 5 values: {vector[:5]}")