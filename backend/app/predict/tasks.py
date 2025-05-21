from celery import Celery
from PIL import Image
import io, base64
import numpy as np
import asyncio, traceback
from app.utils.model import Model
import os

if os.getenv("IS_CELERY_WORKER", "false").lower() == "true":
    model = Model()
else:
    model = None

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    broker_transport_options={'visibility_timeout': 3600},
    result_expires=900 
)

def run_coro(coro):
    """Run a coroutine to completion."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def tolist_safe(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    elif isinstance(x, (list, tuple)):
        return [tolist_safe(i) for i in x]
    elif isinstance(x, dict):
        return {k: tolist_safe(v) for k, v in x.items()}
    else:
        return x

@celery_app.task
def predict_task(file_content, real_radius: float = None, unit: str = 'pixels', conf: float=0.5, iou: float=0.5):
    try:
        image = Image.open(io.BytesIO(file_content)).convert("RGBA")

        # Run the prediction
        masks, overlaid_img, metrics, cdf_chart, is_calibrated = run_coro(
            model.predict(image, real_radius, unit, conf, iou)
        )
        if not is_calibrated:
            unit = "pixels"

        # Convert the overlaid image to base64
        buffer = io.BytesIO()
        Image.fromarray(overlaid_img.astype(np.uint8)).save(buffer, format="PNG")
        overlaid_img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Convert the CDF chart to base64
        chart_buffer = io.BytesIO()
        cdf_chart.save(chart_buffer, format="PNG")
        cdf_chart_b64 = base64.b64encode(chart_buffer.getvalue()).decode("utf-8")

        return {
            "message": "Prediction completed successfully",
            "masks": tolist_safe(masks),
            "overlaid_image": overlaid_img_b64,
            "cdf_chart": cdf_chart_b64,
            "metrics": tolist_safe(metrics),
            "is_calibrated": is_calibrated,
            "unit": unit,
            "conf": conf,
            "iou": iou
        }

    except Exception as e:
        print("Error in predict_task:", e)
        print(traceback.format_exc())
        raise RuntimeError("Prediction task failed") from e
