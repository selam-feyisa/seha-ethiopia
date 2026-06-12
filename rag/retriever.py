import os
import json
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv
from indexer import load_index, embed_text

load_dotenv()

def get_openai_client():
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01"
    )

def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def retrieve(query: str, top_k: int = 4) -> list:
    """
    Takes a user question.
    Returns the top_k most relevant chunks from the index.
    """
    client = get_openai_client()
    index = load_index()

    if not index:
        return []

    # Embed the query
    query_embedding = embed_text(client, query)

    # Score all chunks
    scored = []
    for chunk in index:
        score = cosine_similarity(query_embedding, chunk["embedding"])
        scored.append({
            "source": chunk["source"],
            "text": chunk["text"],
            "score": score
        })

    # Sort by score, return top_k
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]