from fastapi_login import LoginManager
from sqlmodel import Session, select
from passlib.context import CryptContext
from app.models.database import User, get_session
from typing import Optional, Callable, Iterator
import os
import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)

manager = LoginManager(SECRET_KEY, token_url="/api/auth/login")

# Singleton Pattern
class RedisSessionStorage:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisSessionStorage, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__class__._initialized:
            redis_url = os.getenv("REDIS_SESSION_URL", "redis://redis:6380/0")
            self.client = redis.Redis.from_url(redis_url)
            self.__class__._initialized = True

    def set(self, key: str, value: str, ex: int = 600):
        self.client.setex(key, ex, value)

    def get(self, key: str) -> Optional[str]:
        value = self.client.get(key)
        if isinstance(value, bytes):
            return value.decode()
        return None

    def delete(self, key: str):
        self.client.delete(key)


@manager.user_loader(session_provider = get_session)
def load_user(
    username: str, 
    db: Optional[Session] = None,
    session_provider: Optional[Callable[[], Iterator[Session]]] = None
) -> Optional[User]:

    if db is None and session_provider is None:
        raise ValueError("db and session_provider cannot both be None.")

    if db is None and session_provider is not None:
        db = next(session_provider())

    if db is None:
        return None

    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()
    
    return user
