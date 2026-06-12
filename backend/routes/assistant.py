import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../../rag"))
from ask_seha_agent import ask_seha

router = APIRouter()

class AskInput(BaseModel):
    question: str
    language: str = "en"

@router.get("/")
def ask_stub():
    return {"message": "Ask SEHA route is live"}

@router.post("/query")
def query_seha(data: AskInput):
    if not data.question or len(data.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question is too short.")
    try:
        result = ask_seha(data.question, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SEHA agent error: {str(e)}")