from fastapi import APIRouter
router = APIRouter()

@router.get("/prescription")
def prescription_stub():
    return {"status": "ok", "message": "prescription route coming soon"}