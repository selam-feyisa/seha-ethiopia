from fastapi import APIRouter
router = APIRouter()

@app.get("/symptoms")
def symptoms_stub():
    return {"status": "ok", "message": "symptom route coming soon"}