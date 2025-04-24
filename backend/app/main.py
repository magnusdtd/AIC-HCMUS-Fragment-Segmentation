from fastapi import FastAPI
from app.routers.upload import router as upload_router
from app.routers.auth import router as auth_router
from app.routers.predict import router as predict_router
from app.routers.predictions import router as predictions_router

app = FastAPI()

# Include the upload router
app.include_router(upload_router)
# Include the auth router
app.include_router(auth_router)
# Include the predict router
app.include_router(predict_router)
# Include the predictions router
app.include_router(predictions_router)