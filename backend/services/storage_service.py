import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile

STORAGE_DIR = Path(__file__).parent.parent / "storage"

class StorageService:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        
    def save_upload(self, file: UploadFile) -> str:
        """Saves an uploaded file and returns its path relative to storage dir."""
        ext = os.path.splitext(file.filename or "")[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        
        file_path = STORAGE_DIR / unique_name
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return str(file_path)
        
    def get_file_path(self, relative_path: str) -> str:
        return str(STORAGE_DIR / relative_path)
        
    def delete_file(self, relative_path: str):
        path = STORAGE_DIR / relative_path
        if path.exists():
            os.remove(path)
