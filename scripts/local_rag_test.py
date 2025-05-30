"""
Local RAG logic for FMGPT without GUI. Used for testing and development.
"""

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import numpy as np
import requests

# === Konfiguration ===
CHROMA_PATH = "./output/chroma_db"
COLLECTION_NAME = "chunks_semantic"  # Neue Collection mit semantischen Chunks
EMBED_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "mistral"
OLLAMA_URL = "http://localhost:11434/api/generate"
SPRACHE_FILTER = "de"  # Deutsch bevorzugt

# === Chroma-Client starten
print("🔗 Verbinde mit Chroma...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)
embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

# === Eingabe vom Nutzer
frage = input("Deine Frage: ")
frage_embedding = embed_fn([frage])[0]  # einzelne Liste, dann [0] für Vektor

# === Abfrage der relevantesten Chunks
print("🔍 Suche nach passenden Chunks...")
try:
    results = collection.query(
        query_embeddings=[frage_embedding],
        n_results=5,
        where={"sprache": SPRACHE_FILTER}
    )
except Exception as e:
    print(f" Fehler bei der Abfrage: {e}")
    exit(1)

# === Extrahiere relevante Texte
relevante_texte = [
    chunk for chunk in results.get("documents", [[]])[0] if chunk is not None
]

if not relevante_texte:
    print(" Keine relevanten Chunks gefunden.")
    exit(0)

# === Prompt für Ollama aufbauen
prompt = (
    "Du bist ein hilfreicher Fußball-Experte für Football Manager.\n"
    "Nutze den folgenden Kontext, um die Frage zu beantworten.\n"
    "Wenn der Kontext nicht ausreicht, gib dein Bestes anhand deines Wissens.\n\n"
    "Beziehe deine Antworten wenn möglich auf den FM 24.\n\n"
    "KONTEXT:\n"
    + "\n---\n".join(relevante_texte)
    + f"\n\nFRAGE: {frage}\n\nANTWORT:"
)

# === Anfrage an Ollama senden
def ollama_chat(prompt, model=OLLAMA_MODEL):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

print(" Frage an Ollama wird verarbeitet...")
antwort = ollama_chat(prompt)

# === Ausgabe der Antwort
print("\n Antwort von Mistral:\n")
print(antwort)
