import sys
import os
from fastapi import FastAPI, Request, Security, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.routes import symptom, documents, prescription, assistant

# ============================================================
# API KEY AUTH
# ============================================================
API_KEY = os.getenv("SEHA_API_KEY", "seha-dev-key-2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

# ============================================================
# RATE LIMITER
# ============================================================
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SEHA API",
    description="AI Healthcare Assistant for Ethiopia",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# TOKEN BUDGET
# ============================================================
session_token_usage = {}
MAX_TOKENS_PER_SESSION = 5000

@app.middleware("http")
async def token_budget_middleware(request: Request, call_next):
    session_id = request.headers.get("X-Session-ID", get_remote_address(request))

    if request.url.path in ["/ask/query", "/ask/stream"]:
        current_usage = session_token_usage.get(session_id, 0)
        if current_usage >= MAX_TOKENS_PER_SESSION:
            return JSONResponse(
                status_code=429,
                content={"error": "Session limit reached. Please start a new session."}
            )

    response = await call_next(request)

    if request.url.path in ["/ask/query", "/ask/stream"]:
        session_token_usage[session_id] = session_token_usage.get(session_id, 0) + 600

    return response

# ============================================================
# ROUTES
# ============================================================
app.include_router(symptom.router, prefix="/symptoms", tags=["Symptoms"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(prescription.router, prefix="/prescription", tags=["Prescription"])
app.include_router(assistant.router, prefix="/ask", tags=["Assistant"])

@app.get("/")
def root():
    return {"message": "SEHA API is running ✅", "version": "1.0.0"}

@app.get("/session/reset")
def reset_session(request: Request):
    session_id = request.headers.get("X-Session-ID", get_remote_address(request))
    session_token_usage.pop(session_id, None)
    return {"message": "Session reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)