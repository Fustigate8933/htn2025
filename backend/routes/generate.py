from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from services.script_generation import generate_script
from services.avatar_generation import generate_avatar
from services.generate_speech import generate_speech
from services.ppt_processor import PPTProcessor
from utils.gcp import GCSClient
from pydantic import BaseModel
import tempfile
import os
import uuid
import shutil

# Try to import Topview functions, but handle if they're not available
try:
    from utils.Topview import gen_video_batch_simple
    TOPVIEW_AVAILABLE = True
except ImportError:
    print("Topview not available - will use placeholder videos")
    TOPVIEW_AVAILABLE = False

router = APIRouter()
ppt_processor = PPTProcessor()
gcs = GCSClient()

class PresentationRequest(BaseModel):
    ppt_blob: str
    ppt_url: str = None
    face_blob: str
    face_url: str = None
    voice_blob: str
    voice_url: str = None
    style: str = "professional"

@router.post("/presentation")
async def generate_presentation(request: PresentationRequest):
    """
    Generate a complete presentation with slides and avatar videos
    """

    try:
        print("Downloading files from gcs")
        # Download files from GCS
        ppt_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
        face_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        voice_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        try:
            gcs.download_file(request.ppt_blob, ppt_temp.name)
            gcs.download_file(request.face_blob, face_temp.name)
            gcs.download_file(request.voice_blob, voice_temp.name)

            print("Files downloaded from gcs")
            
            presentation_data = ppt_processor.process_presentation(ppt_temp.name, request.style)

            print("Presentation data processed")
            
            if not presentation_data['slides']:
                raise HTTPException(status_code=400, detail="No slides found in PPT file")
            
            # Generate unique presentation ID
            presentation_id = str(uuid.uuid4())
            
            # Generate real avatar videos using batch generation
            try:
                topview_auth = os.getenv('TOPVIEW_AUTH')
                topview_uid = os.getenv('TOPVIEW_UID')
                if not TOPVIEW_AVAILABLE or not topview_auth or not topview_uid:
                    print("Topview not available or environment variables not set, using placeholder videos")
                    video_urls = [f"/api/generated/slide-{i+1}-video.mp4" for i in range(len(presentation_data['slides']))]
                else:
                    print("Topview environment variables found, generating real videos...")
                    video_urls = gen_video_batch_simple(
                        audio_path=voice_temp.name,
                        video_path=face_temp.name,
                        texts=presentation_data['scripts']
                    )
                    
                    # Store videos locally and create accessible URLs
                    local_video_urls = []
                    for i, video_url in enumerate(video_urls):
                        if video_url:
                            local_video_dir = f"generated_videos/{presentation_id}"
                            os.makedirs(local_video_dir, exist_ok=True)
                            local_video_path = f"{local_video_dir}/slide-{i+1}.mp4"
                            try:
                                import requests
                                response = requests.get(video_url)
                                response.raise_for_status()
                                with open(local_video_path, 'wb') as f:
                                    f.write(response.content)
                                accessible_url = f"/api/generated/{presentation_id}/slide-{i+1}.mp4"
                                local_video_urls.append(accessible_url)
                            except Exception as e:
                                print(f"Failed to store video {i+1}: {e}")
                                local_video_urls.append(f"/api/generated/slide-{i+1}-video.mp4")
                        else:
                            local_video_urls.append(f"/api/generated/slide-{i+1}-video.mp4")
                    video_urls = local_video_urls
                    print(f"Successfully generated {len([url for url in video_urls if url])} avatar videos")
            except Exception as avatar_error:
                print(f"Avatar generation failed: {avatar_error}")
                video_urls = [f"/api/generated/slide-{i+1}-video.mp4" for i in range(len(presentation_data['slides']))]
                print("Using placeholder video URLs as fallback")
            
            return {
                "success": True,
                "presentation": {
                    "slides": presentation_data['slides'],
                    "scripts": presentation_data['scripts'],
                    "video_urls": video_urls,
                    "total_slides": presentation_data['total_slides'],
                    "presentation_id": presentation_id
                }
            }
            
        finally:
            # Clean up temporary files
            for temp_file in [ppt_temp.name, face_temp.name, voice_temp.name]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")

@router.get("/generated/{presentation_id}/{filename}")
async def serve_generated_video(presentation_id: str, filename: str):
    """
    Serve locally stored generated videos
    """
    video_path = f"generated_videos/{presentation_id}/{filename}"
    if os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4")
    else:
        raise HTTPException(status_code=404, detail="Video not found")

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
