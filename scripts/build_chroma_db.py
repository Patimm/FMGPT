"""
Script to build the Chroma vector database from text sources for FMGPT.
"""

import os
import json
import math
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

# === Zeichen bereinigen (z. B. ü → u / ungültig → entfernt)
def clean_text(s):
    if isinstance(s, str):
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s

def clean_metadata(meta):
    return {k: clean_text(v) for k, v in meta.items()}

# === Embedding-Funktion vorbereiten
embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# === Chroma initialisieren
client = chromadb.PersistentClient(path=CHROMA_DIR)
if COLLECTION_NAME in [c.name for c in client.list_collections()]:
    client.delete_collection(name=COLLECTION_NAME)
collection = client.create_collection(name=COLLECTION_NAME)

# === Embeddings & Metadaten laden
print(" Lade Embeddings & Metadaten...")
embeddings = np.load(EMBEDDING_FILE)
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadaten = [json.loads(line) for line in f]

assert len(embeddings) == len(metadaten), " Anzahl Embeddings ≠ Anzahl Metadaten!"

# === In Chroma speichern (Batchweise)
print(" Speichere Embeddings in Chroma (bereinigt, batchweise)...")
for i in tqdm(range(0, len(metadaten), BATCH_SIZE), desc="📦 Hinzufügen"):
    batch_meta = metadaten[i:i + BATCH_SIZE]
    batch_emb = embeddings[i:i + BATCH_SIZE]
    batch_ids = [meta["chunk_id"] for meta in batch_meta]
    cleaned_meta = [clean_metadata(m) for m in batch_meta]

    print(" Check: Erste ID im Batch:", batch_ids[0])
    print(" Erste Embedding (shape):", np.array(batch_emb[0]).shape)
    print(" Erste Metadaten:", cleaned_meta[0])

    if any(math.isnan(x) for x in batch_emb[0]):
        print(" Fehler: NaN im ersten Embedding! Abbruch.")
        #print(" Erste Werte:", batch_emb[0][:5])
        exit(1)
    else:
        print(" Embedding ist numerisch stabil.")

    try:
        if batch_ids:  # Sicherheitsprüfung
            collection.add(
                ids=batch_ids,
                embeddings=batch_emb.tolist(),
                metadatas=cleaned_meta
            )
            print(f" Batch {i}–{i+len(batch_meta)-1} gespeichert")
    except Exception as e:
        print(f" Fehler bei Batch {i}–{i+len(batch_meta)-1}: {e}")
        #print(" Beispiel-Metadaten:", cleaned_meta[0])
        break

print(f" Chroma-Datenbank erfolgreich gespeichert unter: {CHROMA_DIR}")

# === Testabfrage
print("\n Testabfrage: 'Wie funktioniert Pressing im Football Manager?'")
try:
    query = "Wie funktioniert Pressing im Football Manager?"
    query_embedding = embed_fn(query)[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=3)

    if results["ids"] and results["ids"][0]:
        print("\n Top 3 ähnliche Chunks:")
        for i, (id_, meta) in enumerate(zip(results["ids"][0], results["metadatas"][0])):
            print(f"{i+1}. {id_} – Thema: {meta['thema']} | Typ: {meta['typ']} | Sprache: {meta['sprache']}")
    else:
        print(" Keine passenden Chunks gefunden.")
except Exception as e:
    print(f" Fehler bei der Testabfrage: {e}")

