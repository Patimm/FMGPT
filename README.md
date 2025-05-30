# 🧠 FMGPT – RAG-gestützter Football Manager Chatbot

FMGPT ist eine moderne Streamlit-Anwendung, die Retrieval-Augmented Generation (RAG) nutzt, um Football-Manager-Fragen mit eigenen Dokumenten und einer lokalen LLM (Ollama) zu beantworten. Die Architektur ist modular, testbar und auf Automatisierung ausgelegt.

## 🚀 Features

- Upload und automatisches Chunking von Textquellen (PDF, TXT, etc.)
- Erstellung und Pflege einer ChromaDB-Vektordatenbank
- Semantische Suche über eingebettete Chunks (Sentence Transformers)
- Kontextuelle RAG-Abfrage mit lokalem LLM (Ollama, z.B. Mistral)
- Interaktives Chat-Interface über Streamlit
- Schutzmechanismen gegen Prompt-Injection (regel- und LLM-basiert)
- Logging und automatisches Speichern des Chatverlaufs
- Modularer, getesteter Python-Code (pytest)

## 🗃️ Projektstruktur

```text
scripts/
├── app.py                  # Hauptanwendung (Streamlit-UI, RAG, LLM)
├── build_chroma_db.py      # Erstellt Vektordatenbank aus Textquellen
├── chunk_texts.py          # Zerlegt Texte in semantische Chunks
├── embed_chunks.py         # Erstellt Embeddings für Chunks
├── prompt_protection.py    # Schutz vor Prompt-Injection
├── logging_utils.py        # Logging-Setup & Event-Logging
├── utils.py                # Hilfsfunktionen (z.B. Chatverlauf speichern)
├── ... weitere Tools & Tests

data/, output/, metadata/   # Arbeits- & Ergebnisverzeichnisse
logs/                       # Logging-Ausgaben & Prompt-Injection-Logs
prompts/Chatverlauf/        # Persistenter Chatverlauf
```

## ⚙️ Setup & Nutzung

1. **Abhängigkeiten installieren**
   ```powershell
   pip install -r requirements.txt
   ```
2. **.env anlegen** (siehe `.env.example`)
3. **ChromaDB aufbauen**
   ```powershell
   python scripts/build_chroma_db.py
   ```
4. **Streamlit-App starten**
   ```powershell
   streamlit run scripts/app.py
   ```
5. **Ollama-Server** (z.B. Mistral) muss lokal laufen

## 🧪 Testen

```powershell
pytest tests/
```

## 🛡️ Sicherheit & Logging
- Schutz vor Prompt-Injection (regel- und LLM-basiert)
- Logging aller kritischen Events und verdächtigen Eingaben
- Persistenter Chatverlauf für Nachvollziehbarkeit

## 📝 Beispiel-Workflow

1. **Eigene Quellen vorbereiten**
   - Lege deine PDF- oder Textdateien im Ordner `data/pdf_data/` ab.

2. **Texte chunking & Embeddings erstellen**
   - Starte das Skript, um die Datenbank zu bauen:
     ```powershell
     python scripts/build_chroma_db.py
     ```
   - Alternativ: Nutze die Einzel-Skripte für Feinschliff (z.B. `chunk_texts.py`, `embed_chunks.py`).

3. **.env konfigurieren**
   - Kopiere `.env.example` zu `.env` und passe ggf. Pfade/Modelle an.

4. **Ollama-Server starten**
   - Stelle sicher, dass Ollama (z.B. Mistral) lokal läuft:
     ```powershell
     ollama run mistral
     ```

5. **Streamlit-App starten**
   - Starte die Chat-Oberfläche:
     ```powershell
     streamlit run scripts/app.py
     ```

6. **Chatten & Ergebnisse prüfen**
   - Stelle Fragen im Web-Interface.
   - Relevante Quellen werden automatisch gesucht und in die Antwort eingebunden.
   - Der Chatverlauf wird gespeichert (`prompts/Chatverlauf/`).

7. **Logs & Sicherheit prüfen**
   - Verdächtige Eingaben werden in `logs/prompt_injection/` protokolliert.
   - Fehler und Systemereignisse findest du in `logs/fmgpt.log`.

8. **Tests ausführen (optional)**
   - Prüfe die Codebasis mit:
     ```powershell
     pytest tests/
     ```

---

> **Tipp:** Für größere Datenmengen oder Anpassungen kannst du die Skripte im `scripts/`-Ordner flexibel kombinieren oder erweitern.



