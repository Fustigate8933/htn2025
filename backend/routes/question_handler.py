from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services.asr import ASRService
from utils.gcp import GCSClient
from utils.audio_preprocess import to_linear16_wav_file
import uuid, os, tempfile
import soundfile as sf

router = APIRouter()
asr = ASRService()
gcs = GCSClient()

@router.post("/audio-to-text")
async def process_question_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="en-US"),
    ppt_url: str = Form(default=None),
    voice_id: str = Form(default=None),
    video_file_id: str = Form(default=None),
    slide_number: int = Form(default=0)
):
    """
    Process uploaded audio file and convert to text using ASR
    """
