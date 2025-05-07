from celery import Celery
from PIL import Image
import io, base64
import numpy as np
import asyncio, traceback
from app.utils.model import model
from app.models.queries import create_prediction
from app.models.database import get_session

celery_app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    broker_transport_options={'visibility_timeout': 3600}
)

def tolist_safe(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    elif isinstance(x, (list, tuple)):
        return [tolist_safe(i) for i in x]
    elif isinstance(x, dict):
        return {k: tolist_safe(v) for k, v in x.items()}
    else:
        return x

def run_coro(coro):
    """Run a coroutine to completion."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@celery_app.task
def predict_task(metadata_id, file_content):
    try:
        db = next(get_session())
        image = Image.open(io.BytesIO(file_content)).convert("RGBA")

        # run the async predict()
        binary_masks, overlaid_img, volumes, is_calibrated = run_coro(
            model.predict(image, conf=0.5, iou=0.5)
        )

        # save prediction to DB
        run_coro(create_prediction(db, metadata_id, binary_masks, volumes, is_calibrated))

        # try to save as PNG; if that fails, assume it's already a base64 string
        try:
            buf = io.BytesIO()
            overlaid_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
        except Exception:
            b64 = overlaid_img if isinstance(overlaid_img, str) else ""

        return {
            "message": "Prediction completed successfully",
            "overlaid_image": b64,
            "volumes": tolist_safe(volumes),
            "is_calibrated": is_calibrated
        }

    except Exception as e:
        print("Error in predict_task:", e)
        print(traceback.format_exc())
        return {
            "message": "Prediction failed",
            "overlaid_image": "",
            "volumes": [],
            "is_calibrated": False
        }