from fastapi import APIRouter, Query, HTTPException
from services.script_generation import generate_script
from services.avatar_generation import generate_avatar
from services.generate_speech import generate_speech
from services.ppt_processor import PPTProcessor
from utils.gcp import GCSClient
import tempfile
import os

router = APIRouter()
ppt_processor = PPTProcessor()
gcs = GCSClient()

@router.post("/presentation")
async def generate_presentation(ppt_blob: str, face_blob: str, voice_blob: str, style: str = "professional"):
    """
    Generate a complete presentation with slides and avatar videos
    """
    try:
        # Download files from GCS
        ppt_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
        face_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        voice_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        try:
            gcs.download_file(ppt_blob, ppt_temp.name)
            gcs.download_file(face_blob, face_temp.name)
            gcs.download_file(voice_blob, voice_temp.name)
            
            presentation_data = ppt_processor.process_presentation(ppt_temp.name, style)
            
            if not presentation_data['slides']:
                raise HTTPException(status_code=400, detail="No slides found in PPT file")
            
            # Generate avator video URLs for every slide
            video_urls = []
            for i, slide in enumerate(presentation_data['slides']):
                video_url = f"/api/generated/slide-{i+1}-video.mp4"
                video_urls.append(video_url)
            
            return {
                "success": True,
                "presentation": {
                    "slides": presentation_data['slides'],
                    "scripts": presentation_data['scripts'],
                    "video_urls": video_urls,
                    "total_slides": presentation_data['total_slides']
                }
            }
            
        finally:
            # Clean up temporary files
            for temp_file in [ppt_temp.name, face_temp.name, voice_temp.name]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")

@router.post("/script")
async def generate_presentation_script(ppt_path: str, voice_sample_path: str):
    script = generate_script(ppt_path, voice_sample_path)
    return {"message": "Script generated successfully", "script": script}

@router.post("/avatar")
async def generate_presentation_avatar(face_image_path: str, voice_sample_path: str, avatar_type: str):
    avatar_path = generate_avatar(face_image_path, voice_sample_path, avatar_type)
    return {"message": "Avatar generated successfully", "avatar_path": avatar_path}

@router.get("/speech")
def get_speech(prompt: str = Query(..., description="输入的文本，比如PPT大纲")):
    text = generate_speech(prompt)
    return {"ok": True, "speech": text}
