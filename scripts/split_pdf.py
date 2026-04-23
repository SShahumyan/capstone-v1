# scripts/split_pdf.py
import pypdf
import os

INPUT_PDF = "D:\capstone_data\Մեղադրական եզրակացություն 62225124.pdf"
OUTPUT_DIR = "D:\capstone_data\data/pdf_batches"
BATCH_SIZE = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

reader = pypdf.PdfReader(INPUT_PDF)
total_pages = len(reader.pages)
print(f"Total pages: {total_pages}")

for start in range(0, total_pages, BATCH_SIZE):
    end = min(start + BATCH_SIZE, total_pages)
    writer = pypdf.PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])
    filename = f"{OUTPUT_DIR}/batch_{start+1:04d}_{end:04d}.pdf"
    with open(filename, "wb") as f:
        writer.write(f)
    print(f"  Saved {filename} ({end - start} pages)")

print("Done")