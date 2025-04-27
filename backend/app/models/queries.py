from app.models.database import User, ImageMetadata
from app.utils.minio import minio_client, BUCKET_NAME
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import UploadFile
import uuid, io

def get_user_by_username(db: Session, username: str) -> User:
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()

def create_user(db: Session, username: str, hashed_password: str) -> User:
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_image_by_user_id(db: Session, user_id: str) -> list:
    statement = select(ImageMetadata).where(ImageMetadata.user_id == user_id)
    images = db.exec(statement).all()
    return images

async def create_img_metadata(db: Session, user: User, file: UploadFile) -> ImageMetadata:  
        # Read the file into memory to calculate its size
        file_content = await file.read()
        file_size = len(file_content)

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}-{file.filename}"

        # Upload the file to MinIO
        minio_client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=unique_filename,
            data=io.BytesIO(file_content),
            length=file_size,
            content_type=file.content_type,
        )

        # Save metadata to PostgreSQL
        metadata = ImageMetadata(
            filename=file.filename,
            content_type=file.content_type,
            size=file_size,
            upload_time=datetime.now(),
            user_id=user.id
        )

        db.add(metadata)
        db.commit()
        db.refresh(metadata)

        return metadata

def generate_presigned_url(object_name: str, expiration: timedelta) -> str:
    try:
        url = minio_client.presigned_get_object(BUCKET_NAME, object_name, expires=expiration)
        return url
    except Exception as e:
        print("Error generating presigned URL: ", e)
        return None
