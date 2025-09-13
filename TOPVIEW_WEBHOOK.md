# Topview Webhook Integration

This document describes the webhook endpoint setup for Topview AI notifications.

## Overview

The `/notice/topview` endpoint serves as a webhook callback for Topview AI to notify your application when video generation tasks are completed.

## Endpoints

### POST `/notice/topview`
Main webhook endpoint that receives notifications from Topview AI.

**Expected Request Format**:
```json
{
  "taskId": "task_12345",
  "status": "success|failed|processing",
  "message": "Optional message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Notice received successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### GET `/notice/topview`
Verification endpoint to check if the webhook is active.

**Response**:
```json
{
  "message": "Topview notice endpoint is active",
  "endpoint": "/notice/topview",
  "methods": ["POST", "GET"],
  "description": "Webhook endpoint for Topview AI notifications"
}
```

### POST `/notice/topview/test`
Test endpoint to simulate a Topview notification.

**Response**:
```json
{
  "success": true,
  "message": "Test notification processed",
  "test_data": {
    "taskId": "test_task_123",
    "status": "success",
    "message": "Test notification received",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Configuration

### Topview Integration
In your Topview utility (`backend/utils/Topview.py`), the webhook URL is configured as:

```python
notice_url="https://410534426f02.ngrok-free.app/notice/topview"
```

### Ngrok Setup
For local development, you'll need to:

1. **Install ngrok**:
   ```bash
   # Download from https://ngrok.com/download
   # Or install via package manager
   ```

2. **Start ngrok tunnel**:
   ```bash
   ngrok http 8000
   ```

3. **Update the notice URL** in `Topview.py` with your ngrok URL:
   ```python
   notice_url="https://your-ngrok-url.ngrok-free.app/notice/topview"
   ```

## Usage

### 1. Start the Backend Server
```bash
cd backend
python main.py
```

### 2. Test the Webhook
```bash
# Test GET endpoint
curl http://localhost:8000/notice/topview

# Test POST endpoint
curl -X POST http://localhost:8000/notice/topview/test
```

### 3. Test with Real Topview Notification
```bash
curl -X POST http://localhost:8000/notice/topview \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "real_task_123",
    "status": "success",
    "message": "Video generation completed",
    "timestamp": "2024-01-01T00:00:00Z"
  }'
```

## Logging

The webhook endpoint logs all received notifications:

```
INFO: Received Topview notice: {'taskId': 'task_123', 'status': 'success'}
INFO: Topview task task_123 status: success
```

## Error Handling

The endpoint handles various error scenarios:

- **Invalid JSON**: Logs the raw data and continues
- **Missing fields**: Uses default values and logs warnings
- **Server errors**: Returns 500 status with error details

## Production Considerations

### Security
- Consider adding authentication/authorization
- Validate webhook signatures if Topview provides them
- Rate limiting to prevent abuse

### Reliability
- Implement retry logic for failed notifications
- Store notifications in database for audit trail
- Monitor webhook endpoint health

### Scaling
- Use message queues for high-volume notifications
- Implement async processing for heavy operations
- Consider webhook endpoint load balancing

## Integration with Avatar Generation

The webhook can be extended to:

1. **Update task status** in your database
2. **Notify users** when videos are ready
3. **Trigger follow-up actions** like email notifications
4. **Update UI** in real-time via WebSocket connections

## Example Extension

```python
@router.post("/notice/topview")
async def topview_notice(request: Request):
    # ... existing code ...
    
    if status == 'success':
        # Update database
        await update_task_status(task_id, 'completed')
        
        # Notify user
        await send_user_notification(task_id)
        
        # Trigger UI update
        await broadcast_websocket_update(task_id)
```

## Troubleshooting

### Common Issues

1. **Webhook not receiving notifications**:
   - Check ngrok tunnel is active
   - Verify URL in Topview configuration
   - Check firewall/network settings

2. **JSON parsing errors**:
   - Check Content-Type headers
   - Verify JSON format from Topview
   - Review error logs

3. **Timeout issues**:
   - Implement async processing
   - Use background tasks
   - Optimize response time

### Debug Commands

```bash
# Check if endpoint is accessible
curl -v http://localhost:8000/notice/topview

# Test with verbose output
curl -X POST http://localhost:8000/notice/topview \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  -v
```
