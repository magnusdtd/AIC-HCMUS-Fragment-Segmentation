from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.models.database import get_session
from app.routers.auth import AuthRouter
from app.models.queries import DatabaseService
from app.predict.tasks import celery_app, predict_task
from app.utils.model import Model
from sqlmodel import Session

class PredictRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post('/upload')(self.upload_image)
        self.router.post('/upload_predict')(self.upload_and_predict)
        self.router.get('/task_status/{task_id}')(self.get_task_status)
        self.router.get('/fetch_prediction/{task_id}')(self.fetch_prediction)
        self.router.get('/get_user_tasks')(self.get_user_tasks)
        self.router.get('/re_predict')(self.get_prediction)

    async def upload_image(self, file: UploadFile, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            username = current_user['user']
            user = DatabaseService.get_user_by_username(db, username)
            metadata = await DatabaseService.create_img_metadata(db, user, file)
            return {'message': 'File uploaded successfully', 'metadata': metadata}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def upload_and_predict(self, file: UploadFile, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            img_metadata = await DatabaseService.create_img_metadata(db, current_user, file)
            content = await file.read()
            async_result = predict_task.delay(content)
            DatabaseService.create_user_task(db=db, user_id=current_user.id, img_metadata_id=img_metadata.id, task_id=async_result.id)
            return {"task_id": async_result.id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_task_status(self, task_id: str, current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            result = celery_app.AsyncResult(task_id)
            return {'status': result.state}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def fetch_prediction(self, task_id: str, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            result = celery_app.AsyncResult(task_id)
            if result.state == 'SUCCESS':
                task_result = result.result
                DatabaseService.create_prediction(
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
            elif result.state in ['PENDING', 'RETRY', 'FAILURE']:
                return {'status': result.state}
            else:
                userTask = DatabaseService.get_user_tasks_by_user_id(db, task_id)
                if not userTask:
                    raise HTTPException(status_code=404, detail="Task not found")
                prediction = DatabaseService.get_prediction_by_task_id(db, userTask.task_id)
                if not prediction:
                    raise HTTPException(status_code=404, detail="Prediction not found")
                img_metadata = DatabaseService.get_img_metadata_by_id(db, userTask.img_id)
                if not img_metadata:
                    raise HTTPException(status_code=404, detail="Image metadata not found")
                img = Model.get_img_from_minio(img_metadata.filename)
                if not img:
                    raise HTTPException(status_code=404, detail="Image not found in MinIO")

                masks, metrics = Model.get_prediction_from_minio(prediction.mask_key, prediction.metrics_key)
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

    def get_user_tasks(self, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            tasks = DatabaseService.get_user_tasks_by_user_id(db, current_user.id)
            if not tasks:
                raise HTTPException(status_code=404, detail="No tasks found for this user")
            return {
                'message': 'Fetched user tasks successfully',
                'tasks': [{'task_id': task.task_id, 'created_at': str(task.created_at)} for task in tasks]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_prediction(self, img_name: str, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            img_metadata = DatabaseService.get_img_metadata_by_id(db, img_name)
            if not img_metadata:
                raise HTTPException(status_code=404, detail="Image metadata not found")
            img = Model.get_img_from_minio(img_metadata.filename)
            if not img:
                raise HTTPException(status_code=404, detail="Image not found in MinIO")
            async_result = predict_task.delay(img)
            return {"task_id": async_result.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

predict_router = PredictRouter().router

