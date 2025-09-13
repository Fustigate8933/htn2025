from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/notice/topview")
async def topview_notice(request: Request):
    """
    Webhook endpoint for Topview AI notifications
    Receives notifications when video generation tasks are completed
    """
    try:
        # Get the request body
        body = await request.body()
        
        # Try to parse as JSON
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            # If not JSON, try to get as text
            data = body.decode('utf-8')
        
        logger.info(f"Received Topview notice: {data}")
        
        # Log the notification details
        if isinstance(data, dict):
            task_id = data.get('taskId', 'unknown')
            status = data.get('status', 'unknown')
            message = data.get('message', '')
            
            logger.info(f"Topview task {task_id} status: {status}")
            if message:
                logger.info(f"Message: {message}")
            
            # Handle different status types
            if status == 'success':
                logger.info(f"Task {task_id} completed successfully")
                # You could add logic here to:
                # - Update database records
                # - Send notifications to users
                # - Trigger follow-up actions
                
            elif status == 'failed':
                logger.error(f"Task {task_id} failed: {message}")
                # Handle failure cases
                
            elif status == 'processing':
                logger.info(f"Task {task_id} is still processing")
                # Handle processing status
                
        else:
            logger.info(f"Received non-JSON notice: {data}")
        
        # Always return success to acknowledge receipt
        return JSONResponse(
            content={
                "success": True,
                "message": "Notice received successfully",
                "timestamp": data.get('timestamp') if isinstance(data, dict) else None
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error processing Topview notice: {e}")
        
        # Return error response
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to process notice"
            },
            status_code=500
        )

@router.get("/notice/topview")
async def topview_notice_get():
    """
    GET endpoint for Topview notice (for testing or verification)
    """
    return JSONResponse(
        content={
            "message": "Topview notice endpoint is active",
            "endpoint": "/notice/topview",
            "methods": ["POST", "GET"],
            "description": "Webhook endpoint for Topview AI notifications"
        },
        status_code=200
    )

@router.post("/notice/topview/test")
async def test_topview_notice():
    """
    Test endpoint to simulate a Topview notification
    """
    test_data = {
        "taskId": "test_task_123",
        "status": "success",
        "message": "Test notification received",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    logger.info(f"Test notification: {test_data}")
    
    return JSONResponse(
        content={
            "success": True,
            "message": "Test notification processed",
            "test_data": test_data
        },
        status_code=200
    )
