from fastapi import APIRouter, UploadFile, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from app.models.database import get_session
from app.routers.auth import AuthRouter
from app.models.queries import DatabaseService
from app.predict.tasks import celery_app, predict_task
from app.utils.model import Model
from sqlmodel import Session
from PIL import Image
import io, base64
import zipfile
import numpy as np

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
        self.router.get('/re_predict')(self.re_predict)
        self.router.get('/get_prediction/{task_id}')(self.get_prediction)
        self.router.get('/download_results/{task_id}')(self.download_results)

    async def _fetch_prediction_data(self, task_id: str, db: Session = Depends(get_session)):

        prediction = DatabaseService.get_prediction_by_task_id(db, task_id)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        masks = DatabaseService.get_mask_from_minio(prediction.mask_key)
        if not masks:
            raise HTTPException(status_code=404, detail="Masks not found in MinIO")
        
        metrics = DatabaseService.get_metric_from_minio(prediction.metrics_key)
        if not metrics:
            raise HTTPException(status_code=404, detail="Metrics not found in MinIO")
        
        img_id = DatabaseService.get_img_id_by_task_id(db, task_id)
        if not img_id:  
            raise HTTPException(status_code=404, detail="Image ID not found for task")

        img_metadata = DatabaseService.get_img_metadata_by_id(db, img_id)
        if not img_metadata:
            raise HTTPException(status_code=404, detail="Image metadata not found")
        
        img = DatabaseService.get_img_from_minio(img_metadata.filename)
        if not img:
            raise HTTPException(status_code=404, detail="Image not found in MinIO")
        
        masks = np.array(masks)
        metrics = np.array(metrics)
        img = Image.open(io.BytesIO(img))

        return prediction, masks, metrics, img

    def _generate_zip_response(self, overlaid_image, cdf_chart, task_id):
        overlaid_buffer = io.BytesIO()
        Image.fromarray(overlaid_image.astype("uint8")).save(overlaid_buffer, format="PNG")
        overlaid_buffer.seek(0)

        cdf_buffer = io.BytesIO()
        cdf_chart.save(cdf_buffer, format="PNG")
        cdf_buffer.seek(0)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("overlaid_image.png", overlaid_buffer.getvalue())
            zip_file.writestr("cdf_chart.png", cdf_buffer.getvalue())
        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=results_{task_id}.zip"},
        )

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

    async def fetch_prediction(self, task_id: str, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            result = celery_app.AsyncResult(task_id)
            if (result.state == 'SUCCESS'):
                task_result = result.result
                await DatabaseService.create_prediction(
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
                raise HTTPException(status_code=500, detail="Unexpected task state")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_tasks(self, img_id: int, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            tasks = DatabaseService.get_user_tasks_by_img_id(db, current_user.id, img_id)
            if not tasks:
                raise HTTPException(status_code=404, detail="No tasks found for this user")

            return {
                'message': 'Fetched user tasks successfully',
                'tasks': [
                    {
                        'task_id': task.task_id,
                        'created_at': str(task.created_at),
                    } for task in tasks
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def re_predict(self, img_name: str = Query(...), db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            img = DatabaseService.get_img_from_minio(img_name)
            if not img:
                raise HTTPException(status_code=404, detail="Image not found in MinIO")
            
            img_metadata = DatabaseService.get_img_metadata_by_name(db, img_name)
            if not img_metadata:
                raise HTTPException(status_code=404, detail="Image metadata not found")
            
            async_result = predict_task.delay(img)

            DatabaseService.create_user_task(db=db, user_id=current_user.id, img_metadata_id=img_metadata.id, task_id=async_result.id)
            if not img:
                raise HTTPException(status_code=404, detail="Image not found in MinIO")
            
            return {"task_id": async_result.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_prediction(self, task_id: str, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:

            prediction, masks, metrics, img = await self._fetch_prediction_data(task_id, db)
            

            overlaid_img = Model.get_overlaid_mask(image=img, masks=masks)
            cdf_chart = Model.draw_cdf_chart(diameters=metrics)

            buffer = io.BytesIO()
            Image.fromarray(overlaid_img.astype(np.uint8)).save(buffer, format="PNG")
            overlaid_img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            chart_buffer = io.BytesIO()
            cdf_chart.save(chart_buffer, format="PNG")
            cdf_chart_b64 = base64.b64encode(chart_buffer.getvalue()).decode("utf-8")

            
            response = {
                'overlaid_image': overlaid_img_b64,
                'cdf_chart': cdf_chart_b64,
                'is_calibrated': prediction.is_calibrated,
            }
            return { 'status': 'success', 'result': response }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def download_results(self, task_id: str, db: Session = Depends(get_session), current_user: dict = Depends(AuthRouter.get_current_user)):
        try:
            _, masks, metrics, img = await self._fetch_prediction_data(task_id, db)
            overlaid_image = Model.get_overlaid_mask(image=img, masks=masks)
            cdf_chart = Model.draw_cdf_chart(diameters=metrics)
            return self._generate_zip_response(overlaid_image, cdf_chart, task_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
predict_router = PredictRouter().router

