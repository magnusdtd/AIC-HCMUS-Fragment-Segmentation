from sqlmodel import Session
from app.models.database import User, Image
from fastapi import HTTPException
import uuid
import numpy as np

def create_user(session: Session, username: str, hashed_password: str) -> User:
  pass

def get_user_by_username(session: Session, username: str) -> User:
  pass

def store_image_metadata(session: Session, user_id: uuid.UUID, bucket_name: str, minio_object_key: str, cdf_data: np.ndarray):
  pass

def get_all_image_metadata_by_user(session: Session, user_id: uuid.UUID) -> list[dict]:
  pass
