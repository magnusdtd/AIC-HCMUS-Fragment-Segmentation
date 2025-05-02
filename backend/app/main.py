from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.models.database import create_db_and_tables
from app.routers.auth import router as auth_router
from app.routers.predict import router as predict_router
from app.routers.display_img import router as display_img_router
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse
import os, anyio

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 1000
    yield

app = FastAPI(lifespan=lifespan)
# app = FastAPI(lifespan=lifespan, default_response_class = ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes, upload routes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(predict_router, prefix="/api", tags=["predict"])
app.include_router(display_img_router, prefix="/api", tags=["display_images"])

# Serve static React files
app.mount("/static", StaticFiles(directory="app/build/static"), name="static")

@app.get("/")
def serve_react():
    return FileResponse("app/build/index.html")

@app.get("/api/hello")
def say_hello():
    return {"message": "Hello from FastAPI!"}

# Catch-all for React routes (SPA)
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    path = f"app/build/{full_path}"
    if os.path.exists(path):
        return FileResponse(path)
    return FileResponse("app/build/index.html")