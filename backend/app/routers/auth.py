from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.models.database import User, get_session
from app.models.queries import DatabaseService
from app.models.database import LoginRequest
from datetime import timedelta
from app.utils.security import pwd_context, manager, ACCESS_TOKEN_EXPIRE_MINUTES

class AuthRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("/current-user")(self.get_current_user)
        self.router.post("/register")(self.register)
        self.router.post("/login")(self.login)
    
    @staticmethod
    def get_current_user(user: User = Depends(manager)):
        print(f"Inside function 'get_current_user', user type is {type(user)}")
        if not user:
            print("Token validation failed: User is None")
            raise HTTPException(status_code=401, detail="Invalid or expired token. Please log in again.")
        print(f"Token validation succeeded. User: {user}")
        return user

    def register(self, user: User, db: Session = Depends(get_session)):
        existing_user = DatabaseService.get_user_by_username(db, user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_password = pwd_context.hash(user.password)
        DatabaseService.create_user(db, user.username, hashed_password)
        return {"message": "User registered successfully."}

    def login(self, request: LoginRequest, db: Session = Depends(get_session)):
        user = DatabaseService.get_user_by_username(db, request.username)
        if not user or not pwd_context.verify(request.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid username or password")

        access_token = manager.create_access_token(
            data={"sub": user.username},
            expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": access_token, "token_type": "bearer"}

auth_router = AuthRouter().router

