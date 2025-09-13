from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from utils.Topview import gen_video_batch_simple
import tempfile
import os
from typing import List
import json

router = APIRouter()

@router.post("/batch-videos")
async def generate_batch_videos(
    audio_file: UploadFile = File(...),
    video_file: UploadFile = File(...),
    texts: str = Form(...),  # JSON string of text list
    max_workers: int = Form(default=3),
    notice_url: str = Form(default=None)
):
    """
    Generate multiple videos with the same audio and video but different text content
    
    Args:
        audio_file: Audio file for voice cloning
        video_file: Video file for avatar
        texts: JSON string containing list of text content
        max_workers: Maximum number of concurrent workers
        notice_url: Optional webhook URL for notifications
    """
    # print(audio_file, video_file, texts)
    # return
    try:
        # Parse texts from JSON string
        try:
            texts_list = json.loads(texts)
            if not isinstance(texts_list, list):
                raise ValueError("Texts must be a list")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for texts")
        
        if not texts_list:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        # Validate file types
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Audio file must be an audio file")
        
        if not video_file.content_type or not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Video file must be a video file")
        
        # Save uploaded files to temporary locations
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}") as audio_temp:
            audio_content = await audio_file.read()
            audio_temp.write(audio_content)
            audio_path = audio_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.filename.split('.')[-1]}") as video_temp:
            video_content = await video_file.read()
            video_temp.write(video_content)
            video_path = video_temp.name
        
        try:
            # Generate batch videos using simple function
            video_urls = gen_video_batch_simple(
                audio_path=audio_path,
                video_path=video_path,
                texts=texts_list
            )
            
            # Prepare response
            successful_videos = [url for url in video_urls if url is not None]
            failed_videos = [i for i, url in enumerate(video_urls) if url is None]
            
            response_data = {
                "success": True,
                "total_videos": len(video_urls),
                "successful_videos": len(successful_videos),
                "failed_videos": len(failed_videos),
                "video_urls": successful_videos
            }
            
            if failed_videos:
                response_data["errors"] = [
                    {
                        "index": i,
                        "text": texts_list[i],
                        "error": "Video generation failed"
                    }
                    for i in failed_videos
                ]
            
            return JSONResponse(content=response_data)
            
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                if os.path.exists(video_path):
                    os.unlink(video_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temp files: {cleanup_error}")
                
    except Exception as e:
        print(f"Batch video generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate batch videos: {str(e)}")

@router.post("/batch-videos-simple")
async def generate_batch_videos_simple(
    audio_file: UploadFile = File(...),
    video_file: UploadFile = File(...),
    texts: str = Form(...)  # JSON string of text list
):
    """
    Simplified batch video generation that returns only video URLs
    """
    try:
        # Parse texts from JSON string
        try:
            texts_list = json.loads(texts)
            if not isinstance(texts_list, list):
                raise ValueError("Texts must be a list")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for texts")
        
        if not texts_list:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        # Validate file types
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Audio file must be an audio file")
        
        if not video_file.content_type or not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Video file must be a video file")
        
        # Save uploaded files to temporary locations
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}") as audio_temp:
            audio_content = await audio_file.read()
            audio_temp.write(audio_content)
            audio_path = audio_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.filename.split('.')[-1]}") as video_temp:
            video_content = await video_file.read()
            video_temp.write(video_content)
            video_path = video_temp.name
        
        try:
            # Generate batch videos (simplified)
            video_urls = gen_video_batch_simple(
                audio_path=audio_path,
                video_path=video_path,
                texts=texts_list
            )
            
            return JSONResponse(content={
                "success": True,
                "total_videos": len(video_urls),
                "video_urls": video_urls
            })
            
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                if os.path.exists(video_path):
                    os.unlink(video_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temp files: {cleanup_error}")
                
    except Exception as e:
        print(f"Simple batch video generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate batch videos: {str(e)}")

@router.get("/batch-videos/test")
async def test_batch_generation():
    """
    Test endpoint to verify batch generation functionality
    """
    return JSONResponse(content={
        "message": "Batch video generation endpoint is active",
        "endpoints": {
            "/batch-videos": "Full batch generation with detailed results",
            "/batch-videos-simple": "Simplified batch generation returning only URLs",
            "/batch-videos/test": "This test endpoint"
        },
        "usage": {
            "audio_file": "Audio file for voice cloning",
            "video_file": "Video file for avatar",
            "texts": "JSON string array of text content",
            "max_workers": "Maximum concurrent workers (optional, default: 3)",
            "notice_url": "Webhook URL for notifications (optional)"
        }
    })
