import os
import numpy as np
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv
from rag.indexer import load_index, embed_text

load_dotenv()

# ============================================================
# CLIENTS
# ============================================================
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX", "seha-health-index"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

embedding_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_KEY"),
    api_version="2024-02-01"
)

EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

# ============================================================
# EMBED QUERY
# ============================================================
def embed_text(text: str) -> list:
    response = embedding_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding

# ============================================================
# HYBRID SEARCH — keyword + vector
# ============================================================
def retrieve(query: str, top_k: int = 5) -> list:
    query_vector = embed_text(query)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="embedding"
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["id", "source", "chunk_id", "text"],
        top=top_k
    )

    chunks = []
    for r in results:
        chunks.append({
            "source": r["source"],
            "chunk_id": r["chunk_id"],
            "text": r["text"],
            "score": r.get("@search.score", 0)
        })

    return chunks