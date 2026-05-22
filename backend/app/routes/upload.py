import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.dependencies.auth import admin_or_superadmin

UPLOAD_DIR = "uploads/players"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/photo")
async def upload_photo(
    file: UploadFile = File(...),
    current: dict = Depends(admin_or_superadmin),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Use JPG, PNG o WebP.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="El archivo supera los 5 MB.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    return {"photo_url": f"/uploads/players/{filename}"}
