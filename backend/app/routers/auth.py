from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock database
mock_users_db = {}

# Mock User class for compatibility
class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

# Mock Session class
class Session:
    pass

def get_session():
    return Session()

# Helper function to create JWT tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# Mock function to simulate getting a user by username
def mock_get_user_by_username(username: str):
    return mock_users_db.get(username)

# Mock function to simulate creating a user
def mock_create_user(username: str, hashed_password: str):
    import uuid
    user_id = uuid.uuid4()
    mock_users_db[username] = {"username": username, "hashed_password": hashed_password, "user_id": user_id}
    print(f"Mock: Created user {username} with ID {user_id}")

# Function to verify the user's access token 
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from mock database
    user_dict = mock_get_user_by_username(username)
    if user_dict is None:
        raise credentials_exception
    
    # Return User object
    return User(user_id=user_dict["user_id"], username=user_dict["username"])

# Register endpoint
@router.post("/register", response_model=dict)
async def register(username: str, password: str):
    # Check if user exists
    existing_user = mock_get_user_by_username(username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password and create user
    hashed_pw = pwd_context.hash(password)
    mock_create_user(username, hashed_pw)
    
    return {"message": "User registered successfully"}

# Login endpoint
@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Retrieve user by username
    user = mock_get_user_by_username(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user["username"]})
    
    return {"access_token": access_token, "token_type": "bearer"}