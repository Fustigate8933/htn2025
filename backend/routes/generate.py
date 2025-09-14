from fastapi import APIRouter, Query, HTTPException
from services.script_generation import generate_script
from services.avatar_generation import generate_avatar
from services.generate_speech import generate_speech
from services.ppt_processor import PPTProcessor
from services.file_to_speech import PPTProcessor as FileToSpeechProcessor
from utils.gcp import GCSClient
from utils.Topview import gen_video_batch
import tempfile
import os
from fastapi import Body

router = APIRouter()
ppt_processor = PPTProcessor()
file_to_speech_processor = FileToSpeechProcessor()
gcs = GCSClient()

@router.post("/presentation")
async def generate_presentation(
    ppt_blob: str = Body(...),
    face_blob: str = Body(...),
    voice_blob: str = Body(None),
    voice_id: str = Body(None),
    voice_choice: str = Body("upload"),
    style: str = Body("professional")
):
    """
    Generate a complete presentation with slides and avatar videos
    """
    print(f"Processing files: ppt={ppt_blob}, face={face_blob}, voice_choice={voice_choice}, style={style}")
    
    try:
        # Create temporary files for downloaded content
        ppt_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
        face_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")

        # Download files from GCS
        gcs.download_file(ppt_blob, ppt_temp.name)
        gcs.download_file(face_blob, face_temp.name)

        # Handle voice based on choice
        if voice_choice == "upload" and voice_blob:
            voice_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            gcs.download_file(voice_blob, voice_temp.name)
            voice_path = voice_temp.name
        elif voice_choice == "existing" and voice_id:
            # Use existing voice ID directly
            voice_path = voice_id
        else:
            raise HTTPException(status_code=400, detail="Invalid voice configuration")

        # scripts = ["this is a", "this is b", "this is c", "this is d"]
        speech_results = file_to_speech_processor.file_to_speech(ppt_temp.name)
        print(f"Generated scripts for {len(speech_results)} slides")

        # Convert speech results to the format expected by the frontend
        slides_data = []
        scripts = []

        for page_num, script_text in speech_results.items():
            slides_data.append({
                'id': page_num,
                'title': f'Slide {page_num}',
                'content': script_text,
                'image': '',  # Will be populated by PPT processor if needed
                'shapes': []
            })
            scripts.append(script_text)

        print(f"Processed {len(slides_data)} slides with scripts")

        # Generate avatar videos using gen_video_batch
        video_urls = gen_video_batch(
            audio_path=voice_path,
            video_path=face_temp.name,
            tts_text=scripts
        )
        print(f"Generated {len(video_urls)} videos")

        # Clean up temporary files
        try:
            os.unlink(ppt_temp.name)
            os.unlink(face_temp.name)
            if voice_choice == "upload" and voice_blob:
                os.unlink(voice_path)
        except:
            pass

        return {
            "success": True,
            "presentation": {
                "slides": slides_data,
                "scripts": scripts,
                "video_urls": video_urls
            }
        }
    except Exception as e:
        print(f"Error in presentation generation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")

@router.post("/script")
async def generate_presentation_script(ppt_path: str, voice_sample_path: str):
    script = generate_script(ppt_path, voice_sample_path)
    return {"message": "Script generated successfully", "script": script}

@router.post("/avatar")
async def generate_presentation_avatar(face_video_path: str, voice_sample_path: str, avatar_type: str):
    avatar_path = generate_avatar(face_video_path, voice_sample_path, avatar_type)
    return {"message": "Avatar generated successfully", "avatar_path": avatar_path}

@router.get("/speech")
def get_speech(prompt: str = Query(..., description="输入的文本，比如PPT大纲")):
    text = generate_speech(prompt)
    return {"ok": True, "speech": text}
