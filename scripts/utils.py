"""
Utility functions for FMGPT.
"""
import os
import json
from typing import List, Tuple

def speichere_chatverlauf(chat_history: List[Tuple[str, str]], chatverlauf_ordner: str = "prompts/Chatverlauf") -> None:
    """
    Speichert den Chatverlauf als JSON-Datei mit fortlaufender Nummerierung im angegebenen Verzeichnis.
    :param chat_history: Liste von (Frage, Antwort)-Tupeln
    :param chatverlauf_ordner: Zielordner für den Chatverlauf
    """
    os.makedirs(chatverlauf_ordner, exist_ok=True)
    vorhandene = [
        int(f.split("_")[-1].split(".")[0])
        for f in os.listdir(chatverlauf_ordner)
        if f.startswith("chat_") and f.endswith(".json")
    ]
    neue_nummer = max(vorhandene) + 1 if vorhandene else 1
    pfad = os.path.join(chatverlauf_ordner, f"chat_{neue_nummer}.json")
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)
