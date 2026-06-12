import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../../cognitive"))
from document_reader import analyze_document

router = APIRouter()

class DocumentInput(BaseModel):
    file_url: str

@router.get("/")
def documents_stub():
    return {"message": "Documents route is live"}

@router.post("/upload")
def upload_document(data: DocumentInput):
    if not data.file_url:
        raise HTTPException(status_code=400, detail="file_url is required")
    try:
        result = analyze_document(data.file_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis error: {str(e)}")