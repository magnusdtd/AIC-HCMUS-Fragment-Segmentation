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
from app.tasks import celery_app, predict_task, tolist_safe

router = APIRouter()

@router.post('/upload')
async def upload_image(
    file: UploadFile, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        username = current_user['user']
        user = get_user_by_username(db, username)

        metadata = await create_img_metadata(db, user, file)

        return {'message': 'File uploaded successfully', 'metadata': metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

##############################################################################################################################################################
# This DO TIEN DAT's task
# Write test cases for all API endpoints of this app in a folder names 'tests' at ROOT_LEVEL.
# Then complete the following code.
# The '/upload_predict' endpoint will be used to upload an image, save artifacts and return id task.
# User will use this id to fetch the prediction.


@router.post('/upload_predict')
async def upload_and_predict(
    file: UploadFile,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        # standard metadata save
        username = current_user['user']
        user = get_user_by_username(db, username)
        metadata = await create_img_metadata(db, user, file)

        # read bytes
        await file.seek(0)
        content = await file.read()

        # fire-and-wait Celery
        async_result = predict_task.delay(metadata.id, content)
        result = async_result.get(timeout=60)   # blocks until worker returns

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@router.get('/fetch_prediction')
def fetch_prediction(
    task_id: str,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        result = celery_app.AsyncResult(task_id)
        if result.state == 'PENDING':
            return {'status': 'pending'}
        elif result.state == 'SUCCESS':
            return {'status': 'success', 'result': result.result}
        else:
            return {'status': result.state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/re_predict')
def get_prediction(
    img_name: str,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        username = current_user['user']
        user = get_user_by_username(db, username)
        metadata = db.query(Prediction).filter(Prediction.img_name == img_name).first()
        if not metadata:
            raise HTTPException(status_code=404, detail="Image not found")
        file_content = fetch_prediction_from_minio(metadata.img_name)
        image = Image.open(io.BytesIO(file_content)).convert('RGBA')
        binary_masks, overlaid_img, volumes, is_calibrated = model.predict(image, conf=0.5, iou=0.5)
        create_prediction(db, metadata.id, binary_masks, volumes, is_calibrated)
        return {
            'message': 'Re-prediction completed successfully',
            'metadata': {
                'img_name': metadata.img_name,
                'update_time': str(metadata.update_time)
            },
            'volumes': tolist_safe(volumes),
            # 'overlaid_image': tolist_safe(overlaid_img), 
            'is_calibrated': is_calibrated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@router.get('/get_prediction_metadata')
def get_prediction_metadata(
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        username = current_user['user']
        user = get_user_by_username(db, username)
        metadata_list = db.query(Prediction).filter(Prediction.user_id == user.id).all()
        if not metadata_list:
            raise HTTPException(status_code=404, detail="No images found for this user")
        result = [
            {
                'img_id': m.img_id,
                'update_time': str(m.update_time)
            } for m in metadata_list
        ]
        return {
            'message': 'Fetched prediction metadata successfully',
            'metadata': result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))