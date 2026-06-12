import os
import json
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01"
    )

def chunk_text(text: str, chunk_size: int = 500) -> list:
    """Split text into overlapping chunks of ~500 words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - 50):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def embed_text(client, text: str) -> list:
    """Get embedding vector for a piece of text."""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def index_documents(pdf_texts: list) -> list:
    """
    Takes a list of {"source": filename, "text": content} dicts.
    Returns a list of chunks with embeddings ready for retrieval.
    """
    client = get_openai_client()
    index = []

    for doc in pdf_texts:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            embedding = embed_text(client, chunk)
            index.append({
                "source": doc["source"],
                "chunk_id": i,
                "text": chunk,
                "embedding": embedding
            })
        print(f"Indexed {len(chunks)} chunks from {doc['source']}")

    return index

def save_index(index: list, path: str = "rag/index.json"):
    """Save the index to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f)
    print(f"Index saved to {path} ({len(index)} chunks)")

def load_index(path: str = "rag/index.json") -> list:
    """Load index from disk."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)