"""
Script to test the FMGPT chatbot logic in isolation.
"""

import os
import openai
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

# === Lade .env oder Key manuell eintragen
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-..."

# === Embedding & Datenbank vorbereiten
CHROMA_DIR = "./output/chroma_db"
COLLECTION_NAME = "chunks"

embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(name=COLLECTION_NAME)

# === Nutzerfrage
frage = input("❓ Deine Frage: ")

# === Schritt 1: Embedding der Frage + Chunk-Retrieval
query_embedding = embed_fn(frage)
results = collection.query(query_embeddings=[query_embedding], n_results=3)

# === Schritt 2: Kontext bauen
context_chunks = [meta["text"] for meta in results["metadatas"][0]]
kontext = "\n\n".join(context_chunks)

# === Schritt 3: Prompt bauen
prompt = f"""Beantworte die folgende Frage anhand des Kontexts.

Kontext:
{kontext}

Frage: {frage}

Antwort:"""

# === Schritt 4: GPT aufrufen
antwort = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Football-Manager-Experte."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

# === Ausgabe
print("\n🤖 Antwort:\n")
print(antwort.choices[0].message.content)
