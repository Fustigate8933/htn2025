from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os, mimetypes, requests

router = APIRouter()

LOCAL_AUDIO_PATH = "/Users/hanyunguo/Downloads/New Folder With Items/question.mp3" 
MODEL = "@cf/openai/whisper"

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN  = os.getenv("CF_API_TOKEN")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
def _guess_content_type(path: str) -> str:
    ctype, _ = mimetypes.guess_type(path)
    if ctype:
        return ctype
    p = path.lower()
    if p.endswith(".wav"):  return "audio/wav"
    if p.endswith(".mp3"):  return "audio/mpeg"
    if p.endswith(".webm"): return "audio/webm"
    return "application/octet-stream"

@router.post("/cloudfare-audio-to-text")
def cloudfare_audio_to_text(audio_path):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise HTTPException(status_code=500, detail="Missing CF_ACCOUNT_ID / CF_API_TOKEN in backend/.env")
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=400, detail=f"Audio not found: {LOCAL_AUDIO_PATH}")

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{MODEL}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": _guess_content_type(LOCAL_AUDIO_PATH)
    }

    try:
        resp = requests.post(url, headers=headers, data=audio_bytes, timeout=180)
        j = resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cloudflare request failed: {e}")

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=j)

    transcript = j.get("result", {}).get("text", "")

    return JSONResponse({"speech-to-text": transcript})
