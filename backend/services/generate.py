from fastapi import APIRouter, Query
from services.generate_speech import generate_speech

router = APIRouter()

@router.get("/speech")
def get_speech(prompt: str = Query(..., description="输入的文本，比如PPT大纲")):
    text = generate_speech(prompt)
    return {"ok": True, "speech": text}
