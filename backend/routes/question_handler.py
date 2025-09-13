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
    language: str = Form(default="en-US")
):
    """
    Process uploaded audio file and convert to text using ASR
    """
    try:
        # Validate file type
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Convert to the required format (16kHz mono WAV)
            wav_path = to_linear16_wav_file(temp_path, target_sr=16000)
            
            # Verify conversion
            with sf.SoundFile(wav_path) as f:
                channels, sample_rate = f.channels, f.samplerate
            if channels != 1 or sample_rate != 16000:
                raise HTTPException(status_code=500, detail=f"Audio conversion failed: channels={channels}, sample_rate={sample_rate}")
            
            # Upload to GCS
            blob_name = f"questions/{uuid.uuid4().hex}.wav"
            gcs.upload_file(wav_path, blob_name)
            gs_uri = f"gs://{os.getenv('GCS_BUCKET')}/{blob_name}"
            url = gcs.generate_signed_url(blob_name, expiration=3600)
            
            # Transcribe using ASR service
            transcript = asr.transcribe_gcs(gs_uri, language_code=language, sample_rate=16000)
            
            if not transcript or not transcript.strip():
                raise HTTPException(status_code=400, detail="No speech detected in audio")
            
            # Generate response to the question
            transcript_clean = transcript.strip()
            responses = [
                f"That's an excellent question about '{transcript_clean}'. Let me elaborate on this important point.",
                f"Thank you for asking about '{transcript_clean}'. This is a crucial aspect that deserves further explanation.",
                f"Great question regarding '{transcript_clean}'. This connects well with what we've been discussing.",
                f"I appreciate you bringing up '{transcript_clean}'. This is a key consideration in our analysis.",
                f"That's a thoughtful question about '{transcript_clean}'. Let me provide some additional context."
            ]
            
            import random
            response = random.choice(responses)
            response += " In the context of our presentation, this relates directly to the current slide and the broader themes we're exploring. I'd be happy to discuss this further and provide more specific examples if you'd like."
            
            return JSONResponse(content={
                "ok": True,
                "success": True,
                "transcript": transcript_clean,
                "response": response,
                "url": url,
                "gsUri": gs_uri,
                "blob": blob_name,
                "language": language
            })
            
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if 'wav_path' in locals() and os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temp files: {cleanup_error}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing error: {str(e)}")

