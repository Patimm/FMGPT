"""
Script for ChromaDB testing utilities for FMGPT.
"""

import chromadb

client = chromadb.PersistentClient(path="./output/chroma_test")
collection = client.get_or_create_collection(name="test")

collection.add(
    ids=["test_001"],
    embeddings=[[0.1] * 384],
    metadatas=[{"thema": "Test", "typ": "pdf", "sprache": "de"}]
)

print(" Test-Eintrag erfolgreich gespeichert.")
