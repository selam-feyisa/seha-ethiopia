from fastapi import APIRouter
router = APIRouter()

@router.get("/documents")
def documents_stub():
    return {"status": "ok", "message": "documents route coming soon"}