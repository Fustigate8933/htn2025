from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile, shutil, os
from backend.utils.gcp import GCSClient
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

from functools import lru_cache
from backend.utils.gcp import GCSClient

@lru_cache(maxsize=1)
def get_gcs() -> GCSClient:
    return GCSClient()

def _save_temp(upload: UploadFile) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{upload.filename}")
    with tmp as f:
        shutil.copyfileobj(upload.file, f)
    return tmp.name

@router.post("/ppt")
async def upload_ppt(file: UploadFile = File(...)):
    path = _save_temp(file)
    try:
        blob = f"ppt/{file.filename}"
        get_gcs().upload_file(path, blob)
        url = get_gcs().generate_signed_url(blob, expiration=3600)
        return {"ok": True, "url": url, "blob": blob}
    finally:
        os.unlink(path)

@router.post("/face")
async def upload_face(file: UploadFile = File(...)):
    path = _save_temp(file)
    try:
        blob = f"face/{file.filename}"
        get_gcs().upload_file(path, blob)
        url = get_gcs().generate_signed_url(blob, expiration=3600)
        return {"ok": True, "url": url, "blob": blob}
    finally:
        os.unlink(path)

@router.post("/voice")
async def upload_voice(file: UploadFile = File(...)):
    path = _save_temp(file)
    try:
        blob = f"voice/{file.filename}"
        get_gcs().upload_file(path, blob)
        url = get_gcs().generate_signed_url(blob, expiration=3600)
        return {"ok": True, "url": url, "blob": blob}
    finally:
        os.unlink(path)