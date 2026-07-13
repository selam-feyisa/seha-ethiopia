"""
Simple Bearer token check for all API routes.

This is intentionally basic (single shared key), matching what Day 26 in
the roadmap asks for: "Simple API key check for now — proper auth can
come later." Swap this for real per-user auth (e.g. JWT/Azure AD B2C)
post-defense if the project continues.
"""
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import API_KEY

bearer_scheme = HTTPBearer(auto_error=False)


def require_api_key(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if not API_KEY:
        # Fail loudly in real deployments, but don't lock out local dev if
        # nobody has set an API_KEY yet.
        return True

    if credentials is None or credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
