# import json
# import os

# INPUT_FOLDER = "data_qg/ocr_output"
# OUTPUT_FILE = "combined_text.txt"

# all_text = []

# for filename in sorted(os.listdir(INPUT_FOLDER)):
#     if filename.endswith(".json"):
#         filepath = os.path.join(INPUT_FOLDER, filename)

#         with open(filepath, "r", encoding="utf-8") as f:
#             data = json.load(f)

#             chunks = data.get("chunks", [])

#             for entry in chunks:
#                 heading = entry.get("heading", "").strip()
#                 text = entry.get("text", "").strip()
#                 page = entry.get("page_number", "")

#                 if not text:
#                     continue  # skip empty text blocks

#                 combined = ""

#                 # ✅ 1. include heading only if it's not empty
#                 if heading:
#                     combined += heading + "\n"

#                 # ✅ 3. cleaner NotebookLM format
#                 combined += f"[Page {page}]\n{text}\n\n"

#                 all_text.append(combined)

# # Write output
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     f.write("".join(all_text))

# print(f"Saved to {OUTPUT_FILE}")

import json
import os
import re

INPUT_FOLDER = "data_qg/ocr_output"
OUTPUT_FILE = "combined_text.txt"

all_text = []

def extract_batch_start(filename):
    match = re.search(r"batch_(\d{4})_(\d{4})", filename)
    if match:
        return int(match.group(1))
    return None

for filename in sorted(os.listdir(INPUT_FOLDER)):
    if filename.endswith(".json"):
        filepath = os.path.join(INPUT_FOLDER, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

            chunks = data.get("chunks", [])
            batch_start = extract_batch_start(filename)

            # Collect page numbers in this batch
            pages = [
                entry.get("page_number")
                for entry in chunks
                if isinstance(entry.get("page_number"), int)
            ]

            # 🔍 Detect if pages are local (1–10)
            is_local_numbering = False
            if pages:
                if max(pages) <= 10:
                    is_local_numbering = True

            for entry in chunks:
                heading = entry.get("heading", "").strip()
                text = entry.get("text", "").strip()
                page = entry.get("page_number")

                if not text:
                    continue

                # ✅ Fix page number only if needed
                if is_local_numbering and isinstance(page, int) and batch_start:
                    page = batch_start + page - 1

                combined = ""

                if heading:
                    combined += heading + "\n"

                combined += f"[Page {page}]\n{text}\n\n"

                all_text.append(combined)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("".join(all_text))

print(f"Saved to {OUTPUT_FILE}")