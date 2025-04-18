from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
  pass

