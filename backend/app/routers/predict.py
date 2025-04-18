from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.models.database import *
from app.routers.auth import get_session, oauth2_scheme

router = APIRouter(prefix="/predict", tags=["predict"])

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """This function check acce"""
    pass

@router.post("/", response_model=dict)
async def predict_image(file: UploadFile = File(...), user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    pass



