from fastapi import APIRouter, Depends
from app.models.database import *
from app.routers.auth import get_session, get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.get("/", response_model=list[dict])
async def get_predictions(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
  pass
