"""
Main Streamlit app for FMGPT: Football Manager RAG Chatbot.
Handles UI, user input, retrieval, and LLM interaction.
"""

import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import requests
import os
import json
from dotenv import load_dotenv  # NEW: load environment variables from .env

from prompt_protection import enthält_prompt_injection, ollama_guard_check, chunk_sicher, logge_verdacht
from utils import speichere_chatverlauf  # moved from local definition
from logging_utils import setup_logging, log_event

# === Load environment variables from .env ===
load_dotenv()

# === Konfiguration ===
CHROMA_PATH = os.getenv("CHROMA_PATH", "./output/chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chunks_semantic")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
SPRACHE_FILTER = os.getenv("SPRACHE_FILTER", "de")

# === Setup ChromaDB + Embedding
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)
embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

# === Session-State initialisieren
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Logging initialisieren ===
setup_logging()

# === UI ===
st.title("⚽ Football Manager Chatbot")

# === Formular: Eingabe + Button zusammen ===
with st.form(key="frage_formular", clear_on_submit=True):
    frage = st.text_input("Deine Frage:")
    abschicken = st.form_submit_button("Frage abschicken")

if abschicken and frage.strip() != "":
    
    if enthält_prompt_injection(frage):
        logge_verdacht(frage, typ="user_input")
        st.error("⚠️ Deine Eingabe enthält potenziell schädliche Anweisungen.")
        st.stop()

    # optional:
    if ollama_guard_check(frage):
        logge_verdacht(frage, typ="user_input_llm_check")
        st.error("⚠️ Diese Eingabe wurde vom KI-Filter als riskant eingestuft.")
        st.stop()
    # === Embedding + Chunk-Suche
    frage_embedding = embed_fn([frage])[0]
    results = collection.query(
        query_embeddings=[frage_embedding],
        n_results=5,
        where={"sprache": SPRACHE_FILTER}
    )
    relevante_texte = [
        chunk for chunk in results.get("documents", [[]])[0] if chunk is not None
    ]

    if not relevante_texte:
        st.warning("⚠️ Keine relevanten Chunks gefunden.")
    else:
        # === Prompt zusammenbauen
        verlauf = ""
        for i, (q, a) in enumerate(st.session_state.chat_history):
            verlauf += f"Frage {i+1}: {q}\nAntwort {i+1}: {a}\n\n"

        prompt = (
            "Du bist ein hilfreicher Fußball-Experte für Football Manager.\n"
            "Nutze den folgenden Kontext, um die Frage zu beantworten.\n"
            "Wenn der Kontext nicht ausreicht, gib dein Bestes anhand deines Wissens.\n\n"
            "Beziehe deine Antworten wenn möglich auf den FM 24.\n\n"
            f"CHATVERLAUF:\n{verlauf}"
            + "KONTEXT:\n"
            + "\n---\n".join(relevante_texte)
            + f"\n\nFRAGE: {frage}\n\nANTWORT:"
        )

        # === Anfrage an Ollama
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            )
            antwort = response.json()["response"]
        except Exception as e:
            log_event(f"Fehler bei der Kommunikation mit Ollama: {e}", level="error")
            st.error(f"Fehler bei der Kommunikation mit Ollama: {e}")
            antwort = "⚠️ Es gab ein Problem mit dem Modell."

        # === Verlauf aktualisieren
        st.session_state.chat_history.append((frage, antwort))
        speichere_chatverlauf(st.session_state.chat_history)

# === Chatverlauf anzeigen
if st.session_state.chat_history:
    st.markdown("### 💬 Verlauf")
    for frage, antwort in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 Du:** {frage}")
        st.markdown(f"**🤖 Bot:** {antwort}")
        st.markdown("---")


