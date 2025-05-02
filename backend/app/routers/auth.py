from fastapi import APIRouter, HTTPException, Depends
from fastapi_login.exceptions import InvalidCredentialsException
from sqlmodel import Session
from app.models.database import User, get_session
from app.models.queries import get_user_by_username, create_user
from app.models.database import LoginRequest
from datetime import timedelta
from app.utils.security import pwd_context, manager, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.get("/current-user")
def get_current_user(user: User = Depends(manager)):
    try:
        return {"message": "Token is valid", "user": user.username}
    except InvalidCredentialsException:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")

@router.post("/register")
def register(user: User, db: Session = Depends(get_session)):
    # Check if the user already exists
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = pwd_context.hash(user.password)
    create_user(db, user.username, hashed_password)
    return {"message": "User registered successfully."}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_session)):
    
    user = get_user_by_username(db, request.username)
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = manager.create_access_token(
        data={"sub": user.username},
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

