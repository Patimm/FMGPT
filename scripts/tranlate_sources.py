import os
import json
from tqdm import tqdm
from deep_translator import GoogleTranslator  # Wechsel von LibreTranslator

# === Konfiguration ===
INPUT_FILE = "./output/extracted_sources.jsonl"
OUTPUT_FILE = "./output/translated_sources.jsonl"
translator = GoogleTranslator(source="en", target="de")  # Kein API-Key nötig

# === Übersetzungsfunktion ===
def translate_text(text):
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"⚠️ Fehler bei Übersetzung: {e}")
        return text  # Fallback: Originaltext

# === Hauptfunktion ===
def main():
    translated_data = []

    with open(INPUT_FILE, "r", encoding="utf-8") as infile:
        for line in tqdm(infile, desc="🌍 Übersetze"):
            entry = json.loads(line)

            if entry.get("sprache", "").lower() == "en":
                translated_text = translate_text(entry["text"])
                entry["text"] = translated_text
                entry["sprache"] = "de"
            translated_data.append(entry)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for item in translated_data:
            json.dump(item, outfile, ensure_ascii=False)
            outfile.write("\n")

    print(f"✅ {len(translated_data)} Einträge in {OUTPUT_FILE} gespeichert.")

# === Einstiegspunkt ===
if __name__ == "__main__":
    main()

