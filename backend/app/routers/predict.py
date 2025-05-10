from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.models.database import get_session, UserTask
from app.routers.auth import get_current_user
from app.models.queries import get_user_by_username, create_img_metadata, get_user_tasks_by_user_id, create_prediction, get_prediction_from_minio, get_prediction_from_minio, get_img_from_minio, get_img_metadata_by_id, get_user_tasks_by_user_id, get_prediction_by_task_id, create_user_task
from sqlmodel import Session
from PIL import Image
from app.predict.tasks import celery_app, predict_task
from app.utils.model import Model

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

@router.post('/upload_predict')
async def upload_and_predict(
    file: UploadFile,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Save metadata
        username = current_user['user']
        user = get_user_by_username(db, username)
        img_metadata = await create_img_metadata(db, user, file)

        # Fire Celery task without waiting for the result
        content = await file.read()
        async_result = predict_task.delay(content)

        create_user_task(
            db=db,
            user_id=user.id,
            img_metadata_id=img_metadata.id,
            task_id=async_result.id,
        )

        return {"task_id": async_result.id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@router.get('/task_status/{task_id}')
def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        print("User trying to get task status")
        result = celery_app.AsyncResult(task_id)
        return {
            'status': result.state,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/fetch_prediction/{task_id}')
def fetch_prediction(
    task_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    print("User trying to get prediction")
    try:
        result = celery_app.AsyncResult(task_id)
        if result.state == 'SUCCESS':
            task_result = result.result 
            create_prediction(
                db=db,
                task_id=task_id,
                masks=task_result.get('masks'),
                metrics=task_result.get('metrics'),
                is_calibrated=task_result.get('is_calibrated')
            )
            response = {
                'overlaid_image': task_result.get('overlaid_image'),
                'cdf_chart': task_result.get('cdf_chart'),
                'is_calibrated': task_result.get('is_calibrated')
            }
            result.forget()
            return {'status': 'success', 'result': response}
        elif result.state == 'PENDING' or result.state == 'RETRY' or result.state == 'FAILURE':
            return {'status': result.state}
        else: # if the task is not found in the celery backend
            userTask = get_user_tasks_by_user_id(db, task_id)
            if not userTask:
                raise HTTPException(status_code=404, detail="Task not found")
            prediction = get_prediction_by_task_id(db, userTask.task_id)
            if not prediction:
                raise HTTPException(status_code=404, detail="Prediction not found")
            img_metadata = get_img_metadata_by_id(db, userTask.img_id)
            if not img_metadata:
                raise HTTPException(status_code=404, detail="Image metadata not found")
            img = get_img_from_minio(img_metadata.filename)
            if not img:
                raise HTTPException(status_code=404, detail="Image not found in MinIO")

            masks, metrics = get_prediction_from_minio(prediction.mask_key, prediction.metrics_key)
            overlaid_image = Model.get_overlaid_mask(img=img, masks=masks)  
            cdf_chart = Model.draw_cdf_chart(diameters=metrics)

            return {
                'status': 'success',
                'result': {
                    'overlaid_image': overlaid_image,
                    'cdf_chart': cdf_chart,
                    'is_calibrated': prediction.is_calibrated,
                }
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/get_user_tasks')
def get_user_tasks(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        username = current_user['user']
        user = get_user_by_username(db, username)
        tasks = get_user_tasks_by_user_id(db, user.id)
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found for this user")
        return {
            'message': 'Fetched user tasks successfully',
            'tasks': [{'task_id': task.task_id, 'created_at': str(task.created_at)} for task in tasks]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/re_predict')
def get_prediction(
    img_name: str,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        img_metadata = get_img_metadata_by_id(db, img_name)
        if not img_metadata:
            raise HTTPException(status_code=404, detail="Image metadata not found")
        img = get_img_from_minio(img_metadata.filename)
        if not img:
            raise HTTPException(status_code=404, detail="Image not found in MinIO")
    
        async_result = predict_task.delay(img)

        return {"task_id": async_result.id}
   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

