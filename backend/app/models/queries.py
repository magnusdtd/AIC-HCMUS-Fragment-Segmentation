from app.models.database import User, ImageMetadata, Prediction
from app.utils.minio import minio_client, BUCKET_NAME
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import UploadFile
import uuid, io, pickle
import numpy as np

def create_user(db: Session, username: str, hashed_password: str) -> User:
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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
            filename=unique_filename,
            content_type=file.content_type,
            size=file_size,
            upload_time=datetime.now(),
            user_id=user.id
        )

        db.add(metadata)
        db.commit()
        db.refresh(metadata)

        file.file.seek(0)

        return metadata

async def create_prediction(
    db: Session, 
    img_id: int, 
    binary_masks: np.ndarray, 
    volumes: np.ndarray, 
    is_calibrated: bool = False
) -> Prediction:
    # Serialize the binary masks and volumes
    serialized_masks = pickle.dumps(binary_masks)
    serialized_volumes = pickle.dumps(volumes)

    # Generate unique object keys for MinIO with img_id and datetime
    timestamp = datetime.now()  # Keep this as a datetime object
    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")  
    binary_mask_key = f"{img_id}_{timestamp_str}_binary_masks.pkl"
    volumes_key = f"{img_id}_{timestamp_str}_volumes.pkl"

    # Upload the serialized data to MinIO
    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=binary_mask_key,
        data=io.BytesIO(serialized_masks),
        length=len(serialized_masks),
        content_type="application/octet-stream",
    )
    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=volumes_key,
        data=io.BytesIO(serialized_volumes),
        length=len(serialized_volumes),
        content_type="application/octet-stream",
    )

    # Create a new Prediction entry with the object keys
    prediction = Prediction(
        id=img_id,
        update_time=timestamp,  # Pass the datetime object here
        binary_mask_key=binary_mask_key,
        volumes_key=volumes_key,
        has_calibrated=is_calibrated
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction

def fetch_prediction_from_minio(binary_mask_key: str, volumes_key: str):
    # Download binary masks from MinIO
    binary_masks_response = minio_client.get_object(BUCKET_NAME, binary_mask_key)
    binary_masks = pickle.loads(binary_masks_response.read())

    # Download volumes from MinIO
    volumes_response = minio_client.get_object(BUCKET_NAME, volumes_key)
    volumes = pickle.loads(volumes_response.read())

    return binary_masks, volumes

def get_user_by_username(db: Session, username: str) -> User:
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()

def get_user_image_by_user_id(db: Session, user_id: str) -> list:
    statement = select(ImageMetadata).where(ImageMetadata.user_id == user_id)
    images = db.exec(statement).all()
    return images
