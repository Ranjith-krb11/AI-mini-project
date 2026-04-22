import chromadb
from chromadb.config import Settings
import os

def get_chroma_client():
    # This ensures the database is saved locally in your data folder
    db_path = os.path.join(os.getcwd(), "data", "chroma_db")
    return chromadb.PersistentClient(path=db_path)

def get_or_create_collection(collection_name="syllabus_data"):
    client = get_chroma_client()
    # Gets the collection if it exists, otherwise creates a new one
    return client.get_or_create_collection(name=collection_name)