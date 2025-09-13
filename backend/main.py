import backend.config
from fastapi import FastAPI
from backend.routes import upload, generate, health, audio_to_text
from backend.services import asr

app = FastAPI(title="Hack the stage API")

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(generate.router, prefix="/generate", tags=["Generate"])
app.include_router(audio_to_text.router,      prefix="/dev",      tags=["Dev"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Hack-the-Stage API"}
