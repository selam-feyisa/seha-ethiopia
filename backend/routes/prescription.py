import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../../cognitive"))
from prescription_ocr import read_prescription

router = APIRouter()

class PrescriptionInput(BaseModel):
    image_url: str

@router.get("/")
def prescription_stub():
    return {"message": "Prescription route is live"}

@router.post("/scan")
def scan_prescription(data: PrescriptionInput):
    if not data.image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
    try:
        result = read_prescription(data.image_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prescription scan error: {str(e)}")