from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ppt_processor import PPTProcessor
from utils.gcp import GCSClient
import tempfile
import os

router = APIRouter()
ppt_processor = PPTProcessor()
gcs = GCSClient()

class PPTProcessRequest(BaseModel):
    ppt_blob: str

@router.post("/process-ppt")
async def process_ppt_simple(request: PPTProcessRequest):
    """
    Simply process PPT file and return slide data
    """
    print(f"Received PPT processing request: {request.ppt_blob}")
    try:
        # Download PPT file from GCS
        ppt_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
        
        try:
            # Download file
            gcs.download_file(request.ppt_blob, ppt_temp.name)
            
            # Process PPT file
            slides_data = ppt_processor.extract_slides(ppt_temp.name)
            
            if not slides_data:
                raise HTTPException(status_code=400, detail="No slides found in PPT file")
            
            return {
                "success": True,
                "slides": slides_data,
                "total_slides": len(slides_data)
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(ppt_temp.name):
                os.unlink(ppt_temp.name)
                
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PPT processing error: {str(e)}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to process PPT: {str(e)}")
