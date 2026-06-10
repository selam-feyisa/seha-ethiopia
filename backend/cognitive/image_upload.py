import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "health-documents")


def upload_to_blob(file_name: str, file_data: bytes) -> str:
    """
    Upload a file to Azure Blob Storage.
    Returns the blob URL.
    """
    try:
        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=file_name
        )

        # Upload the file
        blob_client.upload_blob(file_data, overwrite=True)

        # Return the URL
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{file_name}"
        print(f"✅ Uploaded: {file_name} → {blob_url}")
        return blob_url

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise e