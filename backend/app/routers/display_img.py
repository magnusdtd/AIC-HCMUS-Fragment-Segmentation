from fastapi import APIRouter, HTTPException, Depends, Response
from app.models.database import User, get_session
from app.models.queries import DatabaseService
from app.routers.auth import AuthRouter
from sqlmodel import Session
from mimetypes import guess_type

class DisplayImageRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("/display_images")(self.get_user_images)
        self.router.get("/fetch_image/{filename}")(self.fetch_image)

    def get_user_images(self, db: Session = Depends(get_session), current_user: User = Depends(AuthRouter.get_current_user)):
        print("Inside get_user_images function, current user is ", current_user)
        try:
            images = DatabaseService.get_user_image_by_user_id(db, current_user.id)
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

    def fetch_image(self, filename: str):
        try:
            image_data = DatabaseService.get_img_from_minio(filename)
            if image_data is None:
                raise HTTPException(status_code=404, detail="Image not found")

            mime_type, _ = guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"

            result = Response(content=image_data, media_type=mime_type)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching image: {e}")

display_img_router = DisplayImageRouter().router
