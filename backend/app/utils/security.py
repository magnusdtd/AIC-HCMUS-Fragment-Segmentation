from fastapi_login import LoginManager
from sqlmodel import Session, select
from passlib.context import CryptContext
from app.models.database import User, get_session
from typing import Optional, Callable, Iterator
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)

manager = LoginManager(SECRET_KEY, token_url="/api/auth/login")

@manager.user_loader(session_provider = get_session)
def load_user(
    username: str, 
    db: Optional[Session] = None,
    session_provider: Callable[[], Iterator[Session]] = None
) -> Optional[User]:

    if db is None and session_provider is None:
        raise ValueError("db and session_provider cannot both be None.")

    if db is None:
        db = next(session_provider())

    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()
    return user