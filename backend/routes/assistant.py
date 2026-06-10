from fastapi import APIRouter
router = APIRouter()

@router.get("/ask")
def ask_stub():
    return {"status": "ok", "message": "assistant route coming soon"}