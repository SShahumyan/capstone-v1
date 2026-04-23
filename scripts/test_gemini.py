from google import genai
from google.genai import types
import pathlib
from dotenv import load_dotenv
import os

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Retrieve and encode the PDF byte
filepath = pathlib.Path('data_qg/2_Gevorg Simonyan pastat.pdf')

prompt = "exctract the content of the pdf as text. "
response = client.models.generate_content(
  model="gemini-3-flash-preview",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)