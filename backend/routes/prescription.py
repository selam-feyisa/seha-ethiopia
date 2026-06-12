from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def prescription_stub():
    return {
        "status": "ok",
        "message": "Prescription route is working",
        "data": {
            "drug_name": "Amoxicillin",
            "dose": "500mg",
            "frequency": "3 times daily",
            "duration": "7 days",
            "safety_status": "SAFE"
        }
    }