from fastapi import APIRouter, HTTPException, UploadFile, File
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from cognitive.prescription_ocr import read_prescription
except ImportError as e:
    print(f"Warning: Prescription OCR module not ready yet: {e}")
    read_prescription = None

router = APIRouter(prefix="/prescription", tags=["prescription"])

# General upload endpoint (reuse the same one if possible)
@router.post("/upload")
async def upload_prescription_file(file: UploadFile = File(...)):
    # This can call the same upload_to_blob from image_upload
    from cognitive.image_upload import upload_to_blob
    try:
        url = await upload_to_blob(file)
        return {"url": url}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/scan")
async def scan_prescription_endpoint(data: dict):
    if not data.get("image_url"):
        raise HTTPException(400, detail="image_url is required")
    
    if read_prescription is None:
        raise HTTPException(501, detail="Prescription scanner is still being implemented")
    
    try:
        result = read_prescription(data["image_url"])
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Prescription scan failed: {str(e)}")