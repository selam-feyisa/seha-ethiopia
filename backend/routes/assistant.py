from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def ask_stub():
    return {
        "status": "ok",
        "message": "Assistant route is working",
        "data": {
            "answer": "Malaria is treated with artemisinin-based combination therapy (ACT)",
            "source": "Ethiopian MoH Guidelines 2023",
            "disclaimer": "This is for information only. Always consult a licensed healthcare provider."
        }
    }