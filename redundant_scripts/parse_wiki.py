"""
This file handeles taking articles from wiki.
For that you need to download hywiki-latest-pages-articles.xml.bz2 from https://dumps.wikimedia.org/hywiki/latest/
and then run the follofing command 'wikiextractor hywiki-latest-articles.xml.bz2 -o data/wiki --no-templates --processes 4'
"""
import bz2
import re
import os
import html
import json

INPUT_FILE = "hywiki-latest-pages-articles.xml.bz2"
OUTPUT_FILE = "data/armenian_chunks.json"
MAX_ARTICLES = 2000

os.makedirs("data", exist_ok=True)

def clean_text(text):
    text = html.unescape(text)
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    text = re.sub(r'\[https?://[^\]]+\]', '', text)
    text = re.sub(r"'{2,}", '', text)
    text = re.sub(r'==+[^=]*==+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\|[^\n]*', '', text)
    text = re.sub(r'^\s*[{|!]\s*.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def is_armenian(text):
    armenian_chars = sum(1 for c in text if '\u0531' <= c <= '\u058F')
    return armenian_chars / max(len(text), 1) > 0.3

chunks = []
article_count = 0
inside_text = False
current_text = []
current_title = ""

print("Parsing Wikipedia dump...")

with bz2.open(INPUT_FILE, "rt", encoding="utf-8") as f:
    for line in f:
        if "<title>" in line:
            match = re.search(r"<title>(.*?)</title>", line)
            current_title = match.group(1) if match else ""

        if "<text" in line:
            inside_text = True
            current_text = []
            match = re.search(r"<text[^>]*>(.*)", line)
            if match:
                current_text.append(match.group(1))

        elif inside_text:
            if "</text>" in line:
                current_text.append(line.split("</text>")[0])
                inside_text = False

                full_text = clean_text("\n".join(current_text))

                if (len(full_text) < 200 or
                    "#REDIRECT" in full_text or
                    "#վերահղում" in full_text or
                    not is_armenian(full_text)):
                    continue

                paragraphs = [p.strip() for p in full_text.split('\n\n') if len(p.strip()) > 100]

                if not paragraphs:
                    continue

                for p in paragraphs[:5]:
                    chunks.append({"text": p, "article": current_title})

                article_count += 1

                if article_count % 100 == 0:
                    print(f"  {article_count} articles, {len(chunks)} chunks so far...")

                if article_count >= MAX_ARTICLES:
                    break

            else:
                current_text.append(line)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"\nDone: {article_count} articles → {len(chunks)} chunks saved to {OUTPUT_FILE}")