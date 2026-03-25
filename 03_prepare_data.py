# scripts/03_prepare_data.py
import os

input_dir = "data/texts_reduced"
output_file = "data/armenian_texts.txt"

chunks = []
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
            text = f.read().strip()
            if len(text) > 50:
                chunks.append(text)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n\n".join(chunks))

print(f"Prepared {len(chunks)} chunks")