import os
import json
import numpy as np
import unicodedata
import chromadb
from tqdm import tqdm
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# === Konfiguration ===
EMBEDDING_FILE = "./output/embeddings/embeddings.npy"
METADATA_FILE = "./output/embeddings/metadata.jsonl"
CHROMA_DIR = "./output/chroma_db"
COLLECTION_NAME = "chunks"
BATCH_SIZE = 200

# === Hilfsfunktion zur Zeichenbereinigung ===
def clean_text(s):
    if isinstance(s, str):
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s

def clean_metadata(meta):
    return {k: clean_text(v) for k, v in meta.items()}

# === Chroma initialisieren (neue API) ===
client = chromadb.PersistentClient(path=CHROMA_DIR)

if COLLECTION_NAME in [c.name for c in client.list_collections()]:
    client.delete_collection(name=COLLECTION_NAME)
collection = client.create_collection(name=COLLECTION_NAME)

# === Daten laden ===
print("Lade Embeddings & Metadaten...")
embeddings = np.load(EMBEDDING_FILE)
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadaten = [json.loads(line) for line in f]

assert len(embeddings) == len(metadaten), "Anzahl Embeddings ≠ Metadaten!"

# === Hinzufügen in Chroma (mit Bereinigung + Fortschritt) ===
print("Speichere Embeddings in Chroma (bereinigt, batchweise)...")
for i in tqdm(range(0, len(metadaten), BATCH_SIZE), desc="📦 Hinzufügen"):
    batch_meta = metadaten[i:i + BATCH_SIZE]
    batch_emb = embeddings[i:i + BATCH_SIZE]
    batch_ids = [meta["chunk_id"] for meta in batch_meta]
    cleaned_meta = [clean_metadata(m) for m in batch_meta]
    print("DEBUG START:")
    print("Batchgröße:", len(batch_meta))
    print("IDs:", batch_ids[:3])
    print("Embedding-Shape:", np.array(batch_emb[0]).shape)
    print("Erste Metadaten:", cleaned_meta[0])
    print("DEBUG ENDE")


    try:
        collection.add(
            ids=batch_ids,
            embeddings=batch_emb.tolist(),
            metadatas=cleaned_meta
        )
        print(f"Batch {i}–{i+len(batch_meta)-1} gespeichert")
    except Exception as e:
        print(f"Fehler bei Batch {i}–{i+len(batch_meta)-1}: {e}")
        print("Erste Metadaten (bereinigt):", cleaned_meta[0])
        break

print(f"✅ Fertig! Chroma-Datenbank gespeichert in: {CHROMA_DIR}")

# === Testabfrage ===
print("\n Beispielabfrage: 'Wie funktioniert Pressing im Football Manager?'")
embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
results = collection.query(
    query_embeddings=[embed_fn("Wie funktioniert Pressing im Football Manager?")],
    n_results=3
)

print("\n Top 3 Chunks:")
for i, (id_, meta) in enumerate(zip(results["ids"][0], results["metadatas"][0])):
    print(f"{i+1}. {id_} – Thema: {meta['thema']} | Typ: {meta['typ']} | Sprache: {meta['sprache']}")
