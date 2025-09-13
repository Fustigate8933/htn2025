from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/ppt")
async def upload_ppt(file: UploadFile = File(...)):
    return {"message": "PPT uploaded successfully"}

@router.post("/face")
async def upload_face(file: UploadFile = File(...)):
    return {"message": "Face image uploaded successfully"}

@router.post("/voice")
async def upload_voice(file: UploadFile = File(...)):
    return {"message": "Voice sample uploaded successfully"}