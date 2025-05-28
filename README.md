# 🧠 RAG-gestützter Chatbot mit Streamlit

Dies ist eine Streamlit-Anwendung zur Interaktion mit einem Retrieval-Augmented Generation (RAG) Chatbot. Der Bot nutzt eine eigene ChromaDB-Datenbank, um auf eigene Dokumente zuzugreifen und kontextbezogene Antworten zu generieren.

## 🚀 Features

- Upload und Chunking von Textquellen
- Erstellung einer Chroma-Datenbank
- Semantische Suche über eingebettete Chunks
- Lokale RAG-Abfrage mit LLM
- Interaktives Chat-Interface über Streamlit

## 🗃️ Projektstruktur

```text
scripts/
├── app.py                  # Hauptanwendung für Streamlit
├── build_chroma_db.py      # Erstellt Vektordatenbank aus Text
├── chunk_texts.py          # Zerlegt Texte in semantische Chunks
├── embed_chunks.py         # Erstellt Embeddings für Chunks
├── local_rag_test.py       # Lokale RAG-Logik ohne GUI
├── test_chatbot.py         # Testskript zur Chatbot-Funktion
...
data/, output/, metadata/   # Arbeitsverzeichnisse
