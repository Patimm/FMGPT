import os
import json
import math
import numpy as np
import unicodedata
import chromadb
from tqdm import tqdm
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# === Konfiguration ===
CHUNKED_FILE = "./output/chunks/chunked_sources.jsonl"  # Neue Chunk-Datei als Quelle
CHROMA_DIR = "./output/chroma_db"
COLLECTION_NAME = "chunks_semantic"  # Neuer Name für die Collection
BATCH_SIZE = 200
EMBED_MODEL = "all-MiniLM-L6-v2"

# === Zeichen bereinigen (z. B. ü → u / ungültig → entfernt)
def clean_text(s):
    if isinstance(s, str):
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s

def clean_metadata(meta):
    return {k: clean_text(v) for k, v in meta.items()}

# === Embedding-Funktion vorbereiten
embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

# === Chroma initialisieren
client = chromadb.PersistentClient(path=CHROMA_DIR)
if COLLECTION_NAME in [c.name for c in client.list_collections()]:
    client.delete_collection(name=COLLECTION_NAME)
collection = client.create_collection(name=COLLECTION_NAME)

# === Chunked-Datei einlesen
print(f"\nLese Chunks aus {CHUNKED_FILE}...")
with open(CHUNKED_FILE, "r", encoding="utf-8") as f:
    entries = [json.loads(line) for line in f if line.strip()]

print(f" Gelesen: {len(entries)} Chunks")

# === Embeddings berechnen und in Chroma speichern
print("\nErzeuge Embeddings und speichere in Chroma...")
for i in tqdm(range(0, len(entries), BATCH_SIZE), desc=" Hinzufügen"):
    batch = entries[i:i + BATCH_SIZE]
    texts = [e["text"] for e in batch]
    embeddings = embed_fn(texts)

    batch_ids = [e["chunk_id"] for e in batch]
    metadaten = [clean_metadata({
        "chunk_id": e["chunk_id"],
        "quelle": e.get("quelle", "unbekannt"),
        "typ": e.get("typ", "unspezifiziert"),
        "thema": e.get("thema", ""),
        "sprache": e.get("sprache", "unbekannt")
    }) for e in batch]

    try:
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            metadatas=metadaten,
            documents=texts
        )
    except Exception as e:
        print(f" Fehler bei Batch {i}–{i+len(batch)-1}: {e}")
        break

print(f"\n🚀 Chroma-DB erfolgreich gespeichert unter: {CHROMA_DIR} als Collection '{COLLECTION_NAME}'")

# === Testabfrage ===
test_query = "Wie funktioniert Pressing im Football Manager?"
print(f"\nTestabfrage: '{test_query}'")
query_emb = embed_fn([test_query])[0]
results = collection.query(query_embeddings=[query_emb], n_results=3)

if results["ids"] and results["ids"][0]:
    print("\nTop 3 ähnliche Chunks:")
    for i, (id_, meta, doc) in enumerate(zip(results["ids"][0], results["metadatas"][0], results["documents"][0])):
        print(f"{i+1}. {id_} | Thema: {meta['thema']} | Typ: {meta['typ']} | Sprache: {meta['sprache']}")
        print(f"   Textauszug: {doc[:150]}\n")
else:
    print(" Keine passenden Chunks gefunden.")
