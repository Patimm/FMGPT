"""
Test utilities for FMGPT utils module.
"""

import pytest
from scripts import utils
import os
import json

def test_speichere_chatverlauf(tmp_path):
    """
    Test that speichere_chatverlauf creates a new chat file with correct content.
    """
    chatverlauf_ordner = tmp_path / "Chatverlauf"
    chatverlauf_ordner.mkdir()
    # Simulate existing files
    (chatverlauf_ordner / "chat_1.json").write_text("[]", encoding="utf-8")
    (chatverlauf_ordner / "chat_2.json").write_text("[]", encoding="utf-8")
    chat_history = [("Frage?", "Antwort!")]
    utils.speichere_chatverlauf(chat_history, chatverlauf_ordner=str(chatverlauf_ordner))
    files = list(chatverlauf_ordner.glob("*.json"))
    assert len(files) == 3, "Should create a new chat file"
    with open(sorted(files)[-1], encoding="utf-8") as f:
        data = json.load(f)
    assert data == [["Frage?", "Antwort!"]]

def test_log_event(caplog):
    """
    Test that log_event logs messages at all levels.
    """
    from scripts.logging_utils import log_event
    with caplog.at_level("DEBUG"):
        log_event("Test", level="info")
        log_event("Warn", level="warning")
        log_event("Error", level="error")
        log_event("Debug", level="debug")
    logs = caplog.text
    assert "Test" in logs
    assert "Warn" in logs
    assert "Error" in logs
    assert "Debug" in logs
