import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< Updated upstream
from routes import upload, generate, health, audio_to_text, simple_ppt, question_handler, notice
=======
from routes import upload, generate, health, audio_to_text, simple_ppt, question_handler
>>>>>>> Stashed changes
from services import asr
from services import cloudfare_audio_to_text

app = FastAPI(title="Hack the stage API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(generate.router, prefix="/generate", tags=["Generate"])
app.include_router(audio_to_text.router, prefix="/dev", tags=["Dev"])
app.include_router(simple_ppt.router, prefix="/simple", tags=["Simple"])
app.include_router(question_handler.router, prefix="/questions", tags=["Questions"])
app.include_router(notice.router, prefix="/notice", tags=["Notice"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Hack-the-Stage API"}
