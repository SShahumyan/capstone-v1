from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_question(chunk: str, chunk_id: int, document_id: int) -> dict:
    prompt = f"""Դու հայերեն հարցեր ստեղծող օգնական ես։
Քեզ տրված է հայերեն տեքստի հատված դատական գործի նյութերից։
Ստեղծիր ուղիղ 1 հարց հայերենով, որը՝
- Ուղղակիորեն կապված է տեքստի հիմնական բովանդակության հետ
- Կարող է պատասխանվել այդ տեքստի հիման վրա
- Բնական հայերեն հարց է, ոչ թե արհեստական
- Չի պարունակում տեքստից ուղղակի մեջբերումներ
- Հարցի նպատակը լինելու է ստուգելը՝ այդ հարցը տալով մոդելին այն կվերադարձնի՞ այն տեքստի հատվածը որից որ ստեղծվել է հարցը թե՞ ոչ

Տեքստ՝
{chunk}

Պատասխանիր միայն JSON ձևաչափով, առանց որևէ այլ տեքստի՝
{{"question": "քո հարցը այստեղ"}}"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    parsed = json.loads(raw)

    return {
        "question":   parsed["question"],
        "chunkID":    chunk_id,
        "documentID": document_id,
        "chunk_text": chunk
    }