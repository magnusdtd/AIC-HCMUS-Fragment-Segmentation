from app.models.database import User, ImageMetadata, Prediction, UserTask
from app.utils.minio import minio_client, IMG_BUCKET, MASK_BUCKET, METRICS_BUCKET
from sqlmodel import Session, select
from datetime import datetime
from fastapi import UploadFile
import uuid, io, pickle
import numpy as np

class DatabaseService:
    @staticmethod
    def create_user(db: Session, username: str, hashed_password: str) -> User:
        db_user = User(username=username, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def create_img_metadata(db: Session, user: User, file: UploadFile) -> ImageMetadata:
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

    @staticmethod
    async def create_prediction(db: Session, task_id: str, masks: np.ndarray, metrics: np.ndarray, is_calibrated: bool = False, unit: str = 'pixels', conf: float = 0.5, iou: float = 0.5) -> Prediction:
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
            is_calibrated=is_calibrated,
            unit=unit,
            conf=conf,
            iou=iou
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        statement = select(User).where(User.username == username)
        return db.exec(statement).first()

    @staticmethod
    def get_user_image_by_user_id(db: Session, user_id: str) -> list:
        statement = select(ImageMetadata).where(ImageMetadata.user_id == user_id)
        images = db.exec(statement).all()
        return images

    @staticmethod
    def get_img_metadata_by_id(db: Session, img_id: int) -> ImageMetadata:
        statement = select(ImageMetadata).where(ImageMetadata.id == img_id)
        return db.exec(statement).first()

    @staticmethod
    def get_img_from_minio(filename: str) -> bytes:
        img_response = minio_client.get_object(IMG_BUCKET, filename)
        return img_response.read()

    @staticmethod
    def get_img_from_minio(filename: str) -> bytes:
        img_response = minio_client.get_object(IMG_BUCKET, filename)
        return img_response.read()
    
    @staticmethod
    def get_mask_from_minio(mask_key: str) -> np.ndarray:
        mask_response = minio_client.get_object(MASK_BUCKET, mask_key)
        mask = pickle.loads(mask_response.read())
        return mask
    
    @staticmethod
    def get_metric_from_minio(metrics_key: str):
        metrics_response = minio_client.get_object(METRICS_BUCKET, metrics_key)
        metrics = pickle.loads(metrics_response.read())
        return metrics

    @staticmethod
    def get_user_tasks_by_user_id(db: Session, user_id: int) -> list[UserTask]:
        statement = select(UserTask).where(UserTask.user_id == user_id)
        return db.exec(statement).all()

    @staticmethod
    def get_user_task_by_id(db: Session, task_id: str) -> UserTask:
        statement = select(UserTask).where(UserTask.task_id == task_id)
        return db.exec(statement).first()

    @staticmethod
    def get_prediction_by_task_id(db: Session, task_id: str) -> Prediction:
        statement = select(Prediction).where(Prediction.task_id == task_id)
        return db.exec(statement).first()

    @staticmethod
    def create_user_task(db: Session, user_id: int, img_metadata_id: int, task_id: str) -> UserTask:
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

    @staticmethod
    def get_user_tasks_by_img_id(db: Session, user_id: int, img_id: int):
        return db.query(UserTask).filter(UserTask.user_id == user_id, UserTask.img_id == img_id).all()

    @staticmethod
    def get_img_metadata_by_name(db: Session, filename: str) -> ImageMetadata:
        statement = select(ImageMetadata).where(ImageMetadata.filename == filename)
        return db.exec(statement).first()

    @staticmethod
    def get_img_id_by_task_id(db: Session, task_id: str) -> int:
        statement = select(UserTask).where(UserTask.task_id == task_id)
        user_task = db.exec(statement).first()
        return user_task.img_id if user_task else None