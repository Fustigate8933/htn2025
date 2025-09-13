from fastapi import FastAPI
from routes import upload, generate, health

app = FastAPI(title="Hack the stage API")

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(generate.router, prefix="/generate", tags=["Generate"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Hack-the-Stage API"}