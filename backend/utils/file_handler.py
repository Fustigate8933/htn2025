import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

def save_file(file: UploadFile, file_type: str) -> str:
    os.makedirs(f"{UPLOAD_DIR}/{file_type}", exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{file_type}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path