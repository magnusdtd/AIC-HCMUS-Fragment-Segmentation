from fastapi import APIRouter, HTTPException, Depends, Response
from app.models.database import User, get_session
from app.models.queries import get_user_image_by_user_id, get_user_by_username
from app.routers.auth import get_current_user
from app.utils.minio import minio_client, BUCKET_NAME
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
        # Fetch the image from MinIO
        response = minio_client.get_object(BUCKET_NAME, filename)
        
        # Read the image data
        image_data = response.read()
        
        # Guess the MIME type of the file
        mime_type, _ = guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"  # Fallback MIME type
        
        # Return the image as a streaming response
        result = Response(content=image_data, media_type=mime_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {e}")
