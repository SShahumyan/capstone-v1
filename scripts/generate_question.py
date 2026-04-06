"""
This file is responsible for generatin ground questions having a chunk for later creation of 
ground truth dataset
"""

#import google.generativeai as genai
from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#model = genai.GenerativeModel("gemini-2.5-flash")

def generate_question(chunk: str, article: str, chunk_id: int, article_id: int) -> dict:
    prompt = f"""Դու հայերեն հարցեր ստեղծող օգնական ես։
Քեզ տրված է հայերեն տեքստի հատված Վիքիպեդիայից։
Ստեղծիր ուղիղ 1 հարց հայերենով, որը՝
- Ուղղակիորեն կապված է տեքստի հիմնական բովանդակության հետ
- Կարող է պատասխանվել այդ տեքստի հիման վրա
- Բնական հայերեն հարց է, ոչ թե արհեստական
- Չի պարունակում տեքստից ուղղակի մեջբերումներ
- Հարցի նպատակը լինելու է ստուգելը՝ այդ հարցը տալով մոդելին այն կվերադարձնի՞ այն տեքստի հատվածը որից որ ստեղծվել է տեքստը թե՞ ոչ

Տեքստ՝
{chunk}

Պատասխանիր միայն JSON ձևաչափով, առանց որևէ այլ տեքստի՝
{{"question": "քո հարցը այստեղ"}}"""

    #response = model.generate_content(prompt)
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt)
    raw = response.text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    parsed = json.loads(raw)

    return {
        "question":   parsed["question"],
        "article":    article,
        "articleID":  article_id,
        "chunkID":    chunk_id,
        "chunk_text": chunk
    }

#print(generate_question("testing", "test", 1, 1))