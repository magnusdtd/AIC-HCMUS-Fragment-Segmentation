from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.models.database import create_db_and_tables
from app.routers.auth import auth_router
from app.routers.predict import predict_router
from app.routers.display_img import display_img_router
from app.routers.google_auth import router as google_auth_router
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse
import os, anyio
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 1000
    yield

app = FastAPI(lifespan=lifespan, default_response_class = ORJSONResponse)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "this_is_a_secret"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Include auth routes, upload routes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(predict_router, prefix="/api", tags=["predict"])
app.include_router(display_img_router, prefix="/api", tags=["display_images"])
app.include_router(google_auth_router, prefix="/api/auth", tags=["auth"])

# Serve static React files
app.mount("/assets", StaticFiles(directory="app/build/assets"))

@app.get("/")
def serve_react():
    return FileResponse("app/build/index.html")

# Catch-all for React routes (SPA)
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    path = f"app/build/{full_path}"
    if os.path.exists(path):
        return FileResponse(path)
    return FileResponse("app/build/index.html")