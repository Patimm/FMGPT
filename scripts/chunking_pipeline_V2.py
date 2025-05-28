import os
import json
from tqdm import tqdm
import spacy

# === Konfiguration ===
INPUT_FILES = [
    "output/extracted_sources.jsonl",     # enthält deutsch + englisch
    "output/translated_sources.jsonl"     # enthält nur deutsch
]
OUTPUT_DIR = "./output/chunks"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chunked_sources.jsonl")
MAX_WORDS_PER_CHUNK = 120  # Ziel: semantisch sinnvolle Chunk-Größe (~120 Wörter)

# === spaCy-Modelle vorbereiten (einmal laden)
print("Lade spaCy-Modelle...")
spacy_models = {
    "de": spacy.load("de_core_news_sm"),
    "en": spacy.load("en_core_web_sm")
}

# === Sprachspezifisches Satz-Tokenizing mit spaCy
def tokenize_sentences(text, lang_code):
    nlp = spacy_models.get(lang_code.lower(), spacy_models["en"])  # fallback: englisch
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

# === Chunking-Funktion (semantisch sinnvoll, satzbasiert)
def chunk_text_semantic(text, lang_code, max_words=MAX_WORDS_PER_CHUNK):
    sentences = tokenize_sentences(text, lang_code)
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_len = len(sentence_words)

        if current_len + sentence_len > max_words:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = sentence_words
                current_len = sentence_len
            else:
                chunks.append(sentence)
                current_chunk = []
                current_len = 0
        else:
            current_chunk.extend(sentence_words)
            current_len += sentence_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# === Hauptfunktion zur Verarbeitung aller Dateien
def main():
    chunked_data = []

    for input_file in INPUT_FILES:
        if not os.path.exists(input_file):
            print(f"Datei nicht gefunden: {input_file}")
            continue

        with open(input_file, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc=f"🔪 Chunking {os.path.basename(input_file)}"):
                entry = json.loads(line)
                text = entry.get("text", "")
                sprache = entry.get("sprache", "en")  # fallback: englisch

                if not text.strip():
                    continue  # Leere Texte überspringen

                chunks = chunk_text_semantic(text, sprache)

                for i, chunk in enumerate(chunks):
                    chunked_data.append({
                        "chunk_id": f"{entry.get('id', 'unk')}_{entry.get('typ', 'undef')}_{i+1:03}",
                        "quelle": entry.get("quelle", "unbekannt"),
                        "typ": entry.get("typ", "unspezifiziert"),
                        "thema": entry.get("thema", ""),
                        "sprache": sprache,
                        "text": chunk
                    })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in chunked_data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n{len(chunked_data)} Chunks aus {len(INPUT_FILES)} Datei(en) gespeichert unter: {OUTPUT_FILE}")

# === Einstiegspunkt
if __name__ == "__main__":
    main()
