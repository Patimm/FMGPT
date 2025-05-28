import os
import json
import re
from tqdm import tqdm

# === Konfiguration ===
INPUT_FILE = "./output/extracted_sources.jsonl"
OUTPUT_DIR = "./output/chunks"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chunked_sources.jsonl")

# === Chunking-Funktion (ca. 300 Wörter)
def chunk_text(text, max_words=300):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = []

    for sentence in sentences:
        words = sentence.split()
        if len(" ".join(current + words)) > max_words:
            if current:
                chunks.append(" ".join(current))
                current = words
            else:
                chunks.append(sentence)
        else:
            current += words
    if current:
        chunks.append(" ".join(current))
    return chunks

# === Verarbeitung
def main():
    chunked_data = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="🔪 Chunking"):
            entry = json.loads(line)
            chunks = chunk_text(entry["text"])

            for i, chunk in enumerate(chunks):
                chunked_data.append({
                    "chunk_id": f"{entry['id']}_{entry['typ']}_{i+1:03}",
                    "quelle": entry["quelle"],
                    "typ": entry["typ"],
                    "thema": entry["thema"],
                    "sprache": entry["sprache"],
                    "text": chunk
                })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in chunked_data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f" {len(chunked_data)} Chunks mit eindeutiger ID gespeichert in {OUTPUT_FILE}")

# === Einstiegspunkt
if __name__ == "__main__":
    main()
