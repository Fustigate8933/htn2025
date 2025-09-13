# Hack-the-Stage Workflow Features

## New Features Implemented (T6 & T7)

### T6: Integrated Frontend Workflow
A comprehensive workflow page has been created at `/workflow` that integrates all main functions:

#### Features:
- **Step-by-step workflow** with progress indicator
- **File upload** with real-time status feedback
- **Voice recording** with browser-based microphone access
- **Generation options** with customizable settings
- **Progress tracking** for AI generation steps
- **Preview functionality** for generated content

#### Workflow Steps:
1. **Upload Materials**: PPT, face image, voice sample
2. **Record Voice**: Browser-based voice recording with tips
3. **Generate Content**: AI-powered script and avatar generation
4. **Preview & Present**: Live presentation mode with controls

### T7: Scene Switching & Presentation Mode
A fullscreen presentation mode has been implemented at `/presentation`:

#### Features:
- **Real-time switching** between human and avatar views
- **OBS integration** for professional streaming
- **Keyboard shortcuts** for quick control
- **Camera access** for human mode
- **Customizable avatar positioning** and sizing
- **Fullscreen presentation** with overlay controls

#### Keyboard Shortcuts:
- `ESC`: Exit presentation mode
- `Space`: Play/pause presentation
- `1`: Switch to human mode
- `2`: Switch to avatar mode
- `Arrow Keys`: Navigate slides

## API Endpoints Added

### OBS Integration
- `POST /api/obs/switch-scene`: Switch between avatar and human scenes
- `GET /api/obs/status`: Check OBS connection status

### Backend OBS Routes
- `POST /obs/switch-scene`: Backend OBS scene switching
- `GET /obs/status`: Backend OBS status check

## Setup Instructions

### 1. Environment Configuration
Create a `.env` file in the `backend/` directory with:

```env
# API Keys
COHERE_API_KEY=your_cohere_api_key_here

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET=your-gcs-bucket-name

# OBS WebSocket Configuration
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_obs_websocket_password
```

### 2. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
pnpm install
```

### 3. Start the Application
```bash
# Start both frontend and backend
pnpm run dev
```

### 4. OBS Setup (Optional)
1. Install OBS Studio
2. Enable WebSocket server in OBS:
   - Tools → WebSocket Server Settings
   - Enable WebSocket server
   - Set port to 4455
   - Set password (optional)
3. Create two scenes: "Scene_Avatar" and "Scene_Human"

## Usage

### Basic Workflow
1. Navigate to `/workflow`
2. Upload your materials (PPT, face image, voice sample)
3. Record or upload a voice sample
4. Configure generation options
5. Generate your presentation
6. Preview and present

### Presentation Mode
1. From workflow, click "Start Live Presentation"
2. Use keyboard shortcuts or on-screen controls
3. Switch between human and avatar modes
4. Control OBS scenes if connected

## File Structure

```
app/
├── pages/
│   ├── index.vue          # Updated landing page
│   ├── workflow.vue       # New workflow page (T6)
│   └── presentation.vue   # New presentation mode (T7)
└── components/
    └── NavBar.vue

server/
└── api/
    └── obs/
        └── switch-scene.post.ts  # OBS API endpoint

backend/
├── routes/
│   └── obs.py            # New OBS routes
├── tools/
│   └── obs_control.py    # Updated OBS control
└── main.py               # Updated with OBS routes
```

## Next Steps

The following features are ready for integration when the core AI features (T4 & T5) are implemented:

- Voice cloning integration
- Avatar generation integration
- Real video playback in presentation mode
- Slide deck rendering
- Audio synchronization

## Troubleshooting

### OBS Connection Issues
- Ensure OBS WebSocket server is enabled
- Check port and password configuration
- Verify firewall settings

### Camera Access Issues
- Ensure HTTPS is used (required for camera access)
- Check browser permissions
- Try refreshing the page

### File Upload Issues
- Check file size limits
- Verify file formats
- Ensure backend is running

