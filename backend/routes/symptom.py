from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class SymptomsInput(BaseModel):
    symptoms: List[str]

@router.post("/check")
def check_symptoms(data: SymptomsInput):
    if not data.symptoms:
        raise HTTPException(status_code=400, detail="Symptoms list cannot be empty.")

    # Stub response — will connect to real model in Day 9
    return {
        "predictions": [
            {
                "disease": "Malaria",
                "probability": 72,
                "triage": "HIGH",
                "explanation": "Fever and chills are common signs of malaria in Ethiopia."
            },
            {
                "disease": "Typhoid",
                "probability": 18,
                "triage": "MEDIUM",
                "explanation": "Typhoid may also present with similar symptoms."
            },
            {
                "disease": "Common Cold",
                "probability": 10,
                "triage": "LOW",
                "explanation": "Mild upper respiratory symptoms may indicate a common cold."
            }
        ]
    }