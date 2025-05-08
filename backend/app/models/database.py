from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from datetime import datetime
import os

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

    images: list["ImageMetadata"] = Relationship(back_populates="user")

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

class Prediction(SQLModel, table=True):
    id: int = Field(foreign_key="imagemetadata.id", primary_key=True) 
    update_time: datetime = Field(default_factory=datetime.now(), primary_key=True) 
    binary_mask_key: str = Field(nullable=False)  
    volumes_key: str = Field(nullable=False)  
    has_calibrated: bool = Field(nullable=False)  
