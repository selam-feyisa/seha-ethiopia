import os
import json
import base64

from PyPDF2 import PdfReader
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField,
    SearchFieldDataType, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile,
    SearchField
)
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CLIENTS
# ============================================================
blob_client = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX", "seha-health-index")

index_client = SearchIndexClient(
    endpoint=search_endpoint,
    credential=AzureKeyCredential(search_key)
)

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_key)
)

embedding_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_KEY"),
    api_version="2024-02-01"
)

EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

# ============================================================
# CREATE AZURE AI SEARCH INDEX
# ============================================================
def create_index():
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.Int32),
        SearchableField(name="text", type=SearchFieldDataType.String),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="seha-profile"
        )
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="seha-hnsw")],
        profiles=[VectorSearchProfile(name="seha-profile", algorithm_configuration_name="seha-hnsw")]
    )

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

    try:
        index_client.create_or_update_index(index)
        print(f"Index '{index_name}' created/updated successfully")
    except Exception as e:
        print(f"Index creation error: {e}")

# ============================================================
# LOAD PDFs FROM BLOB STORAGE
# ============================================================
def load_pdfs_from_blob() -> list:
    container_client = blob_client.get_container_client("health-documents")
    blobs = list(container_client.list_blobs())
    print(f"Found {len(blobs)} files in Blob Storage")

    docs = []
    for blob in blobs:
        if not blob.name.endswith(".pdf"):
            continue
        print(f"Loading: {blob.name}")
        blob_data = container_client.download_blob(blob.name).readall()
        try:
            reader = PdfReader(BytesIO(blob_data))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            docs.append({"source": blob.name, "text": text})
            print(f"  Extracted {len(text)} chars from {len(reader.pages)} pages")
        except Exception as e:
            print(f"  Error reading {blob.name}: {e}")
    return docs

# ============================================================
# CHUNK TEXT
# ============================================================
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

# ============================================================
# EMBED TEXT
# ============================================================
def embed_text(text: str) -> list:
    response = embedding_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding

# ============================================================
# INDEX ALL DOCUMENTS
# ============================================================
def index_documents(pdf_texts: list = None) -> int:
    if pdf_texts is None:
        pdf_texts = load_pdfs_from_blob()

    create_index()

    all_chunks = []
    for doc in pdf_texts:
        chunks = chunk_text(doc["text"])
        print(f"Chunking {doc['source']}: {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            all_chunks.append({
                "id": base64.urlsafe_b64encode(f"{doc['source']}_{i}".encode()).decode(),

                "source": doc["source"],
                "chunk_id": i,
                "text": chunk,
                "embedding": embedding
            })

    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        search_client.upload_documents(documents=batch)
        print(f"Uploaded batch {i//batch_size + 1}: {len(batch)} chunks")

    print(f"\nTotal chunks indexed: {len(all_chunks)}")
    return len(all_chunks)

# ============================================================
# SAVE/LOAD LOCAL INDEX (fallback)
# ============================================================
def save_index(index: list, path: str = "rag/index.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f)
    print(f"Local index saved: {len(index)} chunks")

def load_index(path: str = "rag/index.json") -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)