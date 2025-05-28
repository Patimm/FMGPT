import os
import csv
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

# === Konfiguration ===
PDF_DIR = "./data/pdf_data"
OUTPUT_DIR = "./output"
PDF_SOURCE_FILE = "./metadata/sources.csv"
WEB_SOURCE_FILE = "./metadata/web_sources.csv"


os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_csv(filepath):
    for encoding in ["utf-8-sig", "utf-8", "cp1252", "latin-1"]:
        try:
            with open(filepath, newline='', encoding=encoding) as f:
                sample = f.read(2048)
                delimiter = ";" if sample.count(";") > sample.count(",") else ","
                f.seek(0)
                reader = csv.DictReader(f, delimiter=delimiter)
                data = list(reader)
                if not reader.fieldnames:
                    raise ValueError(" Keine Kopfzeile gefunden!")
                print(f" Gelesen mit Encoding: {encoding} und Trennzeichen: '{delimiter}'")
                print(f" Spalten: {reader.fieldnames}")
                return data
        except Exception as e:
            print(f" Fehler mit Encoding {encoding}: {e}")
    raise ValueError(f" Keine lesbare Kodierung für Datei: {filepath}")


# === PDF-Text extrahieren ===
def extract_text_from_pdf(path):
    try:
        doc = fitz.open(path)
        return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        return f"Error reading PDF: {e}"

# === Webseiten-Text extrahieren ===
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        return f"Error fetching URL: {e}"

def main():
    results = []

    # === PDFs aus sources.csv ===
    pdf_sources = read_csv(PDF_SOURCE_FILE)
    print(" Verarbeite PDF-Quellen (sources.csv):")
    for entry in tqdm(pdf_sources):
        typ = entry["typ"].strip().lower()
        if typ != "pdf":
            continue

        filename = os.path.basename(entry["url/filename"].strip().replace('"', ''))
        path = os.path.join(PDF_DIR, filename)

        eintrag = {
            "id": entry["id"],
            "quelle": entry["quelle"],
            "typ": typ,
            "thema": entry["thema"],
            "sprache": entry["sprache"],
            "text": extract_text_from_pdf(path)
        }
        results.append(eintrag)

    # === Webseiten aus web_sources.csv ===
    web_sources = read_csv(WEB_SOURCE_FILE)
    print(" Verarbeite Webquellen (web_sources.csv):")
    for entry in tqdm(web_sources):
        eintrag = {
            "id": entry["id"],
            "quelle": entry["url"],
            "typ": "web",
            "thema": entry["thema"],
            "sprache": entry["sprache"],
            "text": extract_text_from_url(entry["url"])
        }
        results.append(eintrag)

    # === Speicherung der Ergebnisse ===
    output_path = os.path.join(OUTPUT_DIR, "extracted_sources.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for item in results:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n Fertig! Alles gespeichert unter: {output_path}")



# === Ausführen ===
if __name__ == "__main__":
    main()


