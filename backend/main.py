import sys
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Add backend folder to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import routes
from routes import symptom, documents, prescription, assistant
from auth import require_api_key

app = FastAPI(
    title="SEHA API",
    description="AI Healthcare Assistant for Ethiopia",
    version="1.0.0"
)

# Rate limiting — 10 requests/minute per IP on the free endpoints (Day 26)
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
# Allow overriding via env so the deployed frontend origin can be added
# once it's live (Day 30/31) without another code change.
_extra_origins = [o for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", *_extra_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes — all behind the shared API key (Day 26)
_auth = [Depends(require_api_key)]
app.include_router(symptom.router, prefix="/symptoms", tags=["Symptoms"], dependencies=_auth)
app.include_router(documents.router, prefix="/documents", tags=["Documents"], dependencies=_auth)
app.include_router(prescription.router, prefix="/prescription", tags=["Prescription"], dependencies=_auth)
app.include_router(assistant.router, prefix="/ask", tags=["Assistant"], dependencies=_auth)

@app.get("/")
def root():
    return {"message": "SEHA API is running ✅", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)