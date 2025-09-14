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
    Generate a complete presentation with slides and avatar videos (DEMO MODE)
    """
    print(f"DEMO MODE: Processing files: ppt={ppt_blob}, face={face_blob}, voice_choice={voice_choice}, style={style}")
    
    try:
        # DEMO MODE: Simulate 6-second generation delay
        print("DEMO MODE: Simulating generation process...")
        import asyncio
        await asyncio.sleep(6)
        
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

        # DEMO MODE: Process PPT to get actual slide images and content
        print("DEMO MODE: Processing PPT to extract slide images...")
        ppt_result = ppt_processor.process_presentation(ppt_temp.name, style)
        slides_data = ppt_result['slides']
        scripts = ppt_result['scripts']
        
        # If no slides were extracted, use mock data
        if not slides_data:
            print("DEMO MODE: No slides extracted, using mock data")
            scripts = [
                "Welcome to our presentation. Today we'll be discussing the key concepts and important topics.",
                "Let's start with the first major point. This is where we introduce the main ideas and framework.",
                "Moving on to our second topic, we'll explore the practical applications and real-world examples.",
                "Finally, let's conclude with a summary of what we've learned and next steps for implementation."
            ]
            
            slides_data = []
            for i, script_text in enumerate(scripts, 1):
                slides_data.append({
                    'id': i,
                    'title': f'Slide {i}',
                    'content': script_text,
                    'image': '',  # No image for mock slides
                    'shapes': []
                })

        print(f"DEMO MODE: Processed {len(slides_data)} slides with {'real' if ppt_result['slides'] else 'mock'} content")

        # DEMO MODE: Generate video URLs using gen_video_batch (which now returns hardcoded paths and IDs)
        print("DEMO MODE: Calling gen_video_batch to get video URLs and IDs...")
        gen_result = gen_video_batch(
            audio_path=voice_path,
            video_path=face_temp.name,
            tts_text=scripts
        )
        video_urls = gen_result["video_urls"]
        voice_id = gen_result["voice_id"]
        video_file_id = gen_result["video_file_id"]
        print(f"DEMO MODE: Received {len(video_urls)} video URLs from gen_video_batch")
        print(f"DEMO MODE: Received voice_id: {voice_id}")
        print(f"DEMO MODE: Received video_file_id: {video_file_id}")

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
                "video_urls": video_urls,
                "voice_id": voice_id,
                "video_file_id": video_file_id
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
