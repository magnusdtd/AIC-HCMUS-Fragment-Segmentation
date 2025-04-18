from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from app.models.database import *

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
  pass

def get_session():
  pass

@router.post("/register", response_model=dict)
async def register(user: User, session: Session = Depends(get_session)):
  pass

@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
  pass

