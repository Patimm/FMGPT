import json

# === Konfiguration ===
CHUNK_FILE = "./output/chunks/chunked_sources.jsonl"

def main():
    seen = set()
    duplicates = set()
    total = 0

    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total += 1
            entry = json.loads(line)
            chunk_id = entry.get("chunk_id")

            if chunk_id in seen:
                duplicates.add(chunk_id)
            else:
                seen.add(chunk_id)

    print(f" Geprüft: {total} Chunks")
    print(f" Eindeutige IDs: {len(seen)}")

    if duplicates:
        print(f" {len(duplicates)} doppelte chunk_ids gefunden:")
        for d in list(duplicates)[:10]:  # nur erste 10 anzeigen
            print("   →", d)
    else:
        print("Keine Duplikate gefunden.")

if __name__ == "__main__":
    main()
