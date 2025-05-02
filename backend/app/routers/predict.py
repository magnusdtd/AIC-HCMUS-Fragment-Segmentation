from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.models.database import get_session, Prediction
from app.routers.auth import get_current_user
from app.models.queries import get_user_by_username, create_img_metadata, create_prediction, fetch_prediction_from_minio
from app.utils.model import model
from sqlmodel import Session
from datetime import datetime
from PIL import Image
from app.models.queries import create_prediction
import io

router = APIRouter()

@router.post("/upload")
async def upload_image(
    file: UploadFile, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        username = current_user["user"]
        user = get_user_by_username(db, username)

        metadata = await create_img_metadata(db, user, file)

        return {"message": "File uploaded successfully", "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

##############################################################################################################################################################
# This DO TIEN DAT's task
# Write test cases for all API endpoints of this app in a folder names "tests" at ROOT_LEVEL.
# Then complete the following code.
# The "/upload_predict" endpoint will be used to upload an image, save artifacts and return id task.
# User will use this id to fetch the prediction.


@router.post("/upload_predict")
async def upload_and_predict(
    file: UploadFile, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        # Get the current user
        username = current_user["user"]
        user = get_user_by_username(db, username)

        # Store metadata in the database
        metadata = await create_img_metadata(db, user, file)

        # Process the uploaded image
        file_content = await file.read()
        image = Image.open(io.BytesIO(file_content)).convert("RGBA")

        # Perform prediction using the model
        binary_masks, overlaid_img, volumes, is_calibrated = await model.predict(image, conf=0.5, iou=0.5)

        # Store prediction in the database
        await create_prediction(db, metadata.id, binary_masks, volumes, is_calibrated)

        return {
            "message": "Prediction completed successfully",
            "metadata": metadata,
            "volumes": volumes,
            "overlaid_image": overlaid_img,
            "is_calibrated": is_calibrated 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@router.get("/fetch_prediction")
def fetch_prediction(
    task_id: int,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("re_predict")
def get_prediction(
    img_name: str,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
  # User want to re-predict their image. Store new prediction to database.
  try:
      pass
  except Exception as e:
      raise Exception(status_code=500, detail=str(e))
  
@router.get("get_prediction_metadata")
def get_prediction_metadata(
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
  # The frontend will show user all of their images and predictions
  # For each image of an user, server will return all of their prediction .
  # (img_id, update_time)
  try:
      pass
  except Exception as e:
      raise Exception(status_code=500, detail=str(e))


##############################################################################################################################################################