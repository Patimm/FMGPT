import os
import json
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# === Konfiguration ===
CHUNK_FILE = "./output/chunks/chunked_sources.jsonl"
EMBEDDING_DIR = "./output/embeddings"
os.makedirs(EMBEDDING_DIR, exist_ok=True)

# === Modell laden ===
print(" Lade Embedding-Modell...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Embedding erstellen ===
embeddings = []
metadaten = []

print(" Embedding der Chunks läuft...")
with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    for line in tqdm(f):
        chunk = json.loads(line)
        vector = model.encode(chunk["text"], show_progress_bar=False)
        embeddings.append(vector)
        metadaten.append({
            "chunk_id": chunk["chunk_id"],
            "quelle": chunk["quelle"],
            "typ": chunk["typ"],
            "thema": chunk["thema"],
            "sprache": chunk["sprache"]
        })

# === Speicherung ===
embedding_array = np.array(embeddings)
np.save(os.path.join(EMBEDDING_DIR, "embeddings.npy"), embedding_array)

with open(os.path.join(EMBEDDING_DIR, "metadata.jsonl"), "w", encoding="utf-8") as f:
    for item in metadaten:
        json.dump(item, f, ensure_ascii=False)
        f.write("\n")

print(f" Fertig! {len(embeddings)} Embeddings gespeichert unter:")
print(f" {EMBEDDING_DIR}/embeddings.npy")
print(f" {EMBEDDING_DIR}/metadata.jsonl")
