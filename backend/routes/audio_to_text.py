from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.asr import ASRService
from utils.gcp import GCSClient
from utils.audio_preprocess import to_linear16_wav_file
import uuid, os, soundfile as sf

router = APIRouter()
asr = ASRService()
gcs = GCSClient()

# hard code path
LOCAL_AUDIO_PATH = "/Users/hanyunguo/Downloads/New Folder With Items/University of Waterloo.mp3"

@router.post("/local-audio-to-text")
def hardcoded_audio_to_text(lang: str = "en-US"):
# def hardcoded_audio_to_text(lang: str = "cmn-Hans-CN"):
    try:
        if not os.path.exists(LOCAL_AUDIO_PATH):
            raise HTTPException(status_code=400, detail=f"File not found: {LOCAL_AUDIO_PATH}")

        # 统一成单声道·16k PCM16
        wav_path = to_linear16_wav_file(LOCAL_AUDIO_PATH, target_sr=16000)

        with sf.SoundFile(wav_path) as f:
            ch, rate = f.channels, f.samplerate
        if ch != 1 or rate != 16000:
            raise HTTPException(status_code=500, detail=f"Convert failed: channels={ch}, sample_rate={rate}")

        blob = f"voice/dev/{uuid.uuid4().hex}.wav"
        gcs.upload_file(wav_path, blob)
        gs_uri = f"gs://{os.getenv('GCS_BUCKET')}/{blob}"
        url = gcs.generate_signed_url(blob, expiration=3600)

        text = asr.transcribe_gcs(gs_uri, language_code=lang, sample_rate=16000)

        return JSONResponse(content={
            "ok": True,
            "url": url,
            "gsUri": gs_uri,
            "blob": blob,
            "text": text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR error: {e}")
    finally:
        try:
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass
