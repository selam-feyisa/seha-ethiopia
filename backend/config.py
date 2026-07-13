"""
Central config/secrets loader.

Priority:
1. Azure Key Vault (if AZURE_KEY_VAULT_NAME is set) — used in production (App Service)
2. Local .env file — used for local development

This means routes/scripts should import `get_secret` (or the constants below)
instead of calling os.getenv directly, so the same code works locally and
once deployed with Key Vault wired up.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

_KEY_VAULT_NAME = os.getenv("AZURE_KEY_VAULT_NAME")
_vault_client = None

if _KEY_VAULT_NAME:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        _vault_url = f"https://{_KEY_VAULT_NAME}.vault.azure.net"
        _vault_client = SecretClient(vault_url=_vault_url, credential=DefaultAzureCredential())
    except Exception as e:
        # Don't crash the app if Key Vault isn't reachable (e.g. running locally
        # without `az login`) — just fall back to .env and log why.
        print(f"Warning: could not connect to Key Vault '{_KEY_VAULT_NAME}': {e}")
        _vault_client = None


@lru_cache(maxsize=64)
def get_secret(name: str, default: str | None = None) -> str | None:
    """
    Fetch a secret by name. Key Vault secret names can't contain underscores,
    so env var SOME_KEY maps to Key Vault secret 'some-key'.
    """
    if _vault_client is not None:
        try:
            vault_name = name.lower().replace("_", "-")
            return _vault_client.get_secret(vault_name).value
        except Exception as e:
            print(f"Warning: secret '{name}' not found in Key Vault, falling back to .env ({e})")

    return os.getenv(name, default)


# Commonly used secrets — import these instead of re-reading env everywhere.
API_KEY = get_secret("SEHA_API_KEY")  # shared bearer token for our own frontend to call the backend  # shared bearer token for our own frontend to call the backend
AZURE_STORAGE_CONNECTION_STRING = get_secret("AZURE_STORAGE_CONNECTION_STRING")
AZURE_OPENAI_KEY = get_secret("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = get_secret("AZURE_OPENAI_ENDPOINT")
GROQ_API_KEY = get_secret("GROQ_API_KEY")
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = get_secret("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_KEY = get_secret("AZURE_DOCUMENT_INTELLIGENCE_KEY")
AZURE_SEARCH_ENDPOINT = get_secret("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = get_secret("AZURE_SEARCH_KEY")
