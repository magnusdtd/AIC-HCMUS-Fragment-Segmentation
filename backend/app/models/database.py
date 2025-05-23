from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from datetime import datetime
import os
from pydantic import validator
import re

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

async def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)

    google_id: str = Field(index=True, unique=True, nullable=True)  
    email: str = Field(index=True, unique=True, nullable=True)  
    full_name: str = Field(nullable=True)  
    profile_picture: str = Field(nullable=True) 

    images: list["ImageMetadata"] = Relationship(back_populates="user")
    tasks: list["UserTask"] = Relationship(back_populates="user")

    @validator("username")
    def validate_username(cls, value):
        if not (3 <= len(value) <= 50):
            raise ValueError("Username must be between 3 and 50 characters long.")
        if not re.match(r"^\w+$", value):
            raise ValueError("Username can only contain letters, numbers, and underscores.")
        return value

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return value

class LoginRequest(SQLModel):
    username: str
    password: str

class ImageMetadata(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    filename: str = Field(nullable=False)
    content_type: str = Field(nullable=False)
    size: int = Field(nullable=False)
    upload_time: datetime = Field(default_factory=datetime.now())
    user_id: int = Field(foreign_key="user.id", nullable=False)  

    user: "User" = Relationship(back_populates="images")

class UserTask(SQLModel, table=True):
    task_id: str = Field(nullable=False, primary_key=True, unique=True)
    img_id: int = Field(foreign_key="imagemetadata.id", nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    user: "User" = Relationship(back_populates="tasks")

class Prediction(SQLModel, table=True):
    task_id: str = Field(foreign_key="usertask.task_id", primary_key=True)
    mask_key: str = Field(nullable=False)  
    metrics_key: str = Field(nullable=False)  
    is_calibrated: bool = Field(nullable=False)
    unit: str = Field(nullable=False)
    conf: float = Field(nullable=False)
    iou: float = Field(nullable=False)
