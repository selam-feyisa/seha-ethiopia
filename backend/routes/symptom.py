import sys
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# Add ml folder to path so we can import score.py
sys.path.append(os.path.join(os.path.dirname(__file__), "../../ml/symptom_model"))

from score import predict

router = APIRouter()

class SymptomsInput(BaseModel):
    symptoms: List[str]

@router.post("/check")
def check_symptoms(data: SymptomsInput):
    if not data.symptoms:
        raise HTTPException(status_code=400, detail="Symptoms list cannot be empty.")
    try:
        result = predict(data.symptoms)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")