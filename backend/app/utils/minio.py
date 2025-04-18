from minio import Minio
import uuid
from app.models.database import Image

class MinIOClient:
  def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
    pass

  def upload_image(self, user_id: uuid.UUID, image_data: bytes, image_id: uuid.UUID) -> str:
    pass

  def get_presigned_url(self, object_key: str) -> str:
    pass

  def get_images_from_metadata(self, metadata_list: list[dict]) -> list[Image]:
    pass

  