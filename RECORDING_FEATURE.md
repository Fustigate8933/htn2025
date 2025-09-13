# Question Recording Feature

This document describes the question recording feature that allows presenters to record questions and receive AI-generated responses during presentations.

## Features

### Frontend Components

1. **useAudioRecording Composable** (`app/composables/useAudioRecording.ts`)
   - Manages microphone permissions and audio recording
   - Handles audio processing and transcription
   - Provides state management for recording workflow

2. **QuestionRecording Component** (`app/components/QuestionRecording.vue`)
   - UI for recording questions with microphone
   - Audio playback and processing controls
   - Transcript display and response generation
   - Text-to-speech for responses
   - Uses standard CSS instead of Tailwind utilities

### Backend API

1. **Question Processing** (`backend/routes/question_handler.py`)
   - Audio-to-text conversion using Google Cloud Speech-to-Text
   - Response generation (placeholder implementation)
   - File upload and processing

2. **Server API Routes**
   - `/api/question/process` - Process recorded audio and generate response

## How to Use

### During Presentation

1. **Start Recording**: Click "Record Question" button
2. **Speak Your Question**: Press and hold or click to record
3. **Stop Recording**: Click "Stop Recording" when done
4. **Auto-Processing**: Audio is automatically processed to get both transcript and response
5. **Speak Response**: Click "Speak Response" to hear the answer aloud

### Keyboard Shortcuts

- **R**: Toggle recording panel visibility
- **ESC**: Return to preview mode
- **Space**: Play/pause presentation
- **Arrow Keys**: Navigate slides

## Technical Implementation

### Audio Processing Flow

1. **Recording**: Browser MediaRecorder API captures audio
2. **Auto-Processing**: When recording stops, audio is automatically sent to backend
3. **Upload**: Audio file sent to backend via multipart form data
4. **Conversion**: Audio converted to 16kHz mono WAV format
5. **Transcription**: Google Cloud Speech-to-Text processes audio
6. **Response Generation**: Backend generates response based on transcript
7. **Return**: Both transcript and response returned to frontend

### File Structure

```
app/
├── composables/
│   └── useAudioRecording.ts     # Audio recording logic
├── components/
│   └── QuestionRecording.vue    # Recording UI component (standard CSS)
└── pages/
    └── presentation.vue         # Updated with recording panel

server/api/question/
└── process.post.ts              # Combined audio processing and response generation

backend/routes/
└── question_handler.py          # Backend audio processing
```

## Configuration

### Required Environment Variables

- `GCS_BUCKET`: Google Cloud Storage bucket for audio files
- Google Cloud credentials for Speech-to-Text API

### Browser Permissions

- Microphone access required for recording
- Audio permissions handled gracefully with user prompts

## Styling Approach

This implementation avoids Tailwind utility classes like `space-y-4` and uses:

- **Standard CSS**: Custom CSS classes with proper spacing
- **Flexbox**: For layout and alignment
- **CSS Variables**: For consistent theming
- **Responsive Design**: Mobile-friendly layouts

## Future Enhancements

1. **AI Integration**: Replace simple responses with OpenAI/Claude API
2. **Context Awareness**: Use current slide content for better responses
3. **Response Templates**: Customizable response styles
4. **Q&A Logging**: Save questions and responses for review
5. **Multi-language Support**: Support for different languages
6. **Voice Cloning**: Use presenter's voice for responses
7. **Real-time Processing**: Stream audio processing for faster responses

## Troubleshooting

### Common Issues

1. **Microphone Permission Denied**
   - Check browser permissions
   - Ensure HTTPS connection for production

2. **Audio Processing Fails**
   - Verify backend server is running
   - Check Google Cloud credentials
   - Ensure audio file format is supported

3. **Recording Not Working**
   - Test microphone in browser settings
   - Check for conflicting audio applications
   - Verify MediaRecorder API support

### Debug Information

- Check browser console for detailed error messages
- Backend logs show audio processing status
- Network tab shows API request/response details

## API Endpoints

### POST /api/question/process
Process recorded audio and generate response in one call.

**Request**: Multipart form data with audio file
**Response**: 
```json
{
  "success": true,
  "transcript": "Your question text",
  "response": "Generated response text",
  "audio_url": "signed_url_to_audio_file"
}
```
