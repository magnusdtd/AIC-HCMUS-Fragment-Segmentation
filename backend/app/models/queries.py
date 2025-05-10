from app.models.database import User, ImageMetadata, Prediction, UserTask
from app.utils.minio import minio_client, IMG_BUCKET, MASK_BUCKET, METRICS_BUCKET
from sqlmodel import Session, select
from datetime import datetime
from fastapi import UploadFile
import uuid, io, pickle
import numpy as np

def create_user(
    db: Session, 
    username: str, 
    hashed_password: str
) -> User:
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def create_img_metadata(
    db: Session, 
    user: User, 
    file: UploadFile
) -> ImageMetadata:  
    file_content = await file.read()
    file_size = len(file_content)

    unique_filename = f"{uuid.uuid4()}-{file.filename}"

    minio_client.put_object(
        bucket_name=IMG_BUCKET,
        object_name=unique_filename,
        data=io.BytesIO(file_content),
        length=file_size,
        content_type=file.content_type,
    )

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
    task_id: str, 
    masks: np.ndarray, 
    metrics: np.ndarray, 
    is_calibrated: bool = False
) -> Prediction:
    serialized_masks = pickle.dumps(masks)
    serialized_metrics = pickle.dumps(metrics)

    timestamp = datetime.now()  
    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")  
    binary_mask_key = f"{task_id}_{timestamp_str}_masks.pkl"
    metrics_key = f"{task_id}_{timestamp_str}_metrics.pkl"

    minio_client.put_object(
        bucket_name=MASK_BUCKET,
        object_name=binary_mask_key,
        data=io.BytesIO(serialized_masks),
        length=len(serialized_masks),
        content_type="application/octet-stream",
    )
    minio_client.put_object(
        bucket_name=METRICS_BUCKET,
        object_name=metrics_key,
        data=io.BytesIO(serialized_metrics),
        length=len(serialized_metrics),
        content_type="application/octet-stream",
    )

    prediction = Prediction(
        task_id=task_id,
        mask_key=binary_mask_key,
        metrics_key=metrics_key,
        has_calibrated=is_calibrated
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction

def get_prediction_from_minio(mask_key: str, metrics_key: str):
    masks_response = minio_client.get_object(MASK_BUCKET, mask_key)
    masks = pickle.loads(masks_response.read())

    metrics_response = minio_client.get_object(METRICS_BUCKET, metrics_key)
    metrics = pickle.loads(metrics_response.read())

    return masks, metrics

def get_user_by_username(db: Session, username: str) -> User:
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()

def get_user_image_by_user_id(db: Session, user_id: str) -> list:
    statement = select(ImageMetadata).where(ImageMetadata.user_id == user_id)
    images = db.exec(statement).all()
    return images

def get_img_metadata_by_id(db: Session, img_id: int) -> ImageMetadata:
    statement = select(ImageMetadata).where(ImageMetadata.id == img_id)
    return db.exec(statement).first()

def get_img_from_minio(filename: str) -> bytes:
    img_response = minio_client.get_object(IMG_BUCKET, filename)
    return img_response.read()

def get_user_tasks_by_user_id(db: Session, user_id: int) -> list[UserTask]:
    statement = select(UserTask).where(UserTask.user_id == user_id)
    return db.exec(statement).all()

def get_user_task_by_id(db: Session, task_id: str) -> UserTask:
    statement = select(UserTask).where(UserTask.task_id == task_id)
    return db.exec(statement).first()

def get_prediction_by_task_id(db: Session, task_id: str) -> Prediction:
    statement = select(Prediction).where(Prediction.task_id == task_id)
    return db.exec(statement).first()

def create_user_task(
    db: Session, 
    user_id: int, 
    img_metadata_id: int, 
    task_id: str
) -> UserTask:
    user_task = UserTask(
        task_id=task_id,
        img_id=img_metadata_id,
        user_id=user_id,
        created_at=datetime.now()
    )
    db.add(user_task)
    db.commit()
    db.refresh(user_task)
    return user_task
