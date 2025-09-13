# Frontend-Backend Integration Guide

This document explains how the frontend and backend are now connected for the presentation generation workflow.

## Overview

The integration connects the frontend workflow with the backend services to:
1. Extract slides from PowerPoint files
2. Generate scripts for each slide
3. Create avatar videos using batch generation
4. Present the final presentation with both avatar and human modes

## Architecture

```
Frontend (Nuxt.js)          Backend (FastAPI)
├── Upload Step             ├── PPT Processing
├── Generate Step           ├── Script Generation (Cohere)
└── Presentation Step       ├── Avatar Generation (TopView)
                            └── Batch Video Generation
```

## Key Changes Made

### 1. Backend Fixes
- **Fixed `Topview.py`**: Added missing `gen_video_batch_simple()` function and fixed syntax errors
- **Updated `main.py`**: Included `batch_generate` route for batch video generation
- **Enhanced batch generation**: Added proper error handling and progress tracking

### 2. Frontend Integration
- **Updated `useWorkflow.ts`**: Modified `generateContent()` to use the new batch generation flow
- **Created new API endpoint**: `/server/api/generate/batch-videos.post.ts` for batch video generation
- **Enhanced presentation page**: Added proper video URL handling and loading states

### 3. New Workflow
1. **PPT Processing**: Extract slides and content from uploaded PowerPoint
2. **Script Generation**: Create scripts for each slide using slide content
3. **Batch Video Generation**: Generate avatar videos for all slides simultaneously
4. **Presentation**: Display slides with avatar videos in presentation mode

## API Endpoints

### Backend Endpoints
- `GET /health` - Health check
- `POST /simple/process-ppt` - Process PowerPoint file
- `POST /batch/batch-videos` - Generate multiple avatar videos
- `GET /batch/batch-videos/test` - Test batch generation endpoint

### Frontend API Endpoints
- `GET /api/health` - Frontend health check
- `POST /api/simple/process-ppt` - Process PPT (proxies to backend)
- `POST /api/generate/batch-videos` - Batch video generation (proxies to backend)

## Usage Flow

### 1. Upload Files
- Upload PowerPoint file (.pptx)
- Upload face video file (.mp4)
- Upload voice audio file (.wav/.mp3)

### 2. Generate Content
When "Generate Content" is clicked:
1. Frontend calls `/api/simple/process-ppt` to extract slides
2. Scripts are generated for each slide
3. Frontend calls `/api/generate/batch-videos` with:
   - Voice file for TTS
   - Face video for avatar
   - Array of scripts for each slide
4. Backend generates avatar videos using TopView API
5. Progress is tracked and displayed in real-time

### 3. Presentation
- Navigate to presentation mode
- Switch between avatar and human modes
- Control slide navigation and playback
- Avatar videos play automatically for each slide

## Environment Setup

### Backend Requirements
```bash
cd backend
pip install -r requirements.txt
```

Required environment variables:
- `TOPVIEW_AUTH` - TopView API authentication
- `TOPVIEW_UID` - TopView user ID
- `COHERE_API_KEY` - Cohere API key for script generation

### Frontend Requirements
```bash
npm install
```

## Running the Application

### 1. Start Backend
```bash
cd backend
python main.py
```
Backend runs on `http://localhost:8000`

### 2. Start Frontend
```bash
npm run dev
```
Frontend runs on `http://localhost:3000`

### 3. Test Integration
```bash
python test_integration.py
```

## File Structure

```
├── backend/
│   ├── main.py                    # Updated with batch_generate route
│   ├── routes/
│   │   ├── batch_generate.py      # Batch video generation endpoint
│   │   └── simple_ppt.py          # PPT processing endpoint
│   ├── services/
│   │   ├── generate_speech.py     # Cohere script generation
│   │   └── avatar_generation.py   # Avatar generation service
│   └── utils/
│       └── Topview.py             # Fixed with batch functions
├── server/api/
│   └── generate/
│       └── batch-videos.post.ts   # New frontend API endpoint
├── app/
│   ├── composables/
│   │   └── useWorkflow.ts         # Updated generation flow
│   └── pages/
│       └── presentation.vue       # Enhanced video handling
└── test_integration.py            # Integration test script
```

## Error Handling

The integration includes comprehensive error handling:
- Backend connectivity checks
- File upload validation
- Generation progress tracking
- Video availability checks
- Fallback UI states

## Troubleshooting

### Common Issues

1. **Backend not accessible**
   - Ensure backend is running on port 8000
   - Check environment variables are set
   - Verify TopView API credentials

2. **Batch generation fails**
   - Check TopView API quota and limits
   - Verify file formats (video: mp4, audio: wav/mp3)
   - Check network connectivity to TopView

3. **Frontend API errors**
   - Ensure frontend is running on port 3000
   - Check CORS settings in backend
   - Verify file uploads are successful

### Debug Mode
Enable debug logging by checking browser console and backend logs for detailed error information.

## Future Enhancements

- Real-time progress updates via WebSocket
- Video generation queue management
- Multiple avatar options
- Advanced presentation controls
- Export functionality

