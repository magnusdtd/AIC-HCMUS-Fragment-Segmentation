from fastapi import APIRouter, HTTPException, Depends, Response
from app.models.database import User, get_session
from app.models.queries import get_user_image_by_user_id, get_user_by_username, get_img_from_minio
from app.routers.auth import get_current_user
from app.utils.minio import minio_client, IMG_BUCKET
from sqlmodel import Session
from mimetypes import guess_type

router = APIRouter()

@router.get("/display_images")
def get_user_images(
    db: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    try:
        username = current_user["user"]
        user = get_user_by_username(db, username)
        images = get_user_image_by_user_id(db, user.id)
        result = {
            "images": [
                {
                    "id": image.id,
                    "filename": image.filename,
                    "size": image.size,
                    "upload_time": image.upload_time,
                }
                for image in images
            ]
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fetch_image/{filename}")
def fetch_image(filename: str):
    try:
        image_data = get_img_from_minio(filename)
        if image_data is None:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Guess the MIME type of the file
        mime_type, _ = guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"  # Fallback MIME type
        
        # Return the image as a streaming response
        result = Response(content=image_data, media_type=mime_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {e}")
