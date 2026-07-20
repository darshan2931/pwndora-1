import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile

STORAGE_DIR = Path(__file__).parent.parent / "storage"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

_storage_dir_created = False

class StorageService:
    def __init__(self):
        global _storage_dir_created
        if not _storage_dir_created:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            _storage_dir_created = True

    def save_upload(self, file: UploadFile) -> str:
        """Saves an uploaded file with byte-level size enforcement. Returns absolute path."""
        ext = os.path.splitext(file.filename or "")[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = STORAGE_DIR / unique_name

        try:
            with open(file_path, "wb") as buffer:
                total_bytes = 0
                while True:
                    chunk = file.file.read(8192)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE:
                        buffer.close()
                        os.remove(file_path)
                        raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)}MB")
                    buffer.write(chunk)
        except Exception:
            if file_path.exists():
                os.remove(file_path)
            raise
        finally:
            try:
                file.file.close()
            except Exception:
                pass

        return str(file_path)

    def get_file_path(self, relative_path: str) -> str:
        return str(STORAGE_DIR / relative_path)

    def delete_file(self, relative_path: str):
        path = STORAGE_DIR / relative_path
        if path.exists():
            os.remove(path)
