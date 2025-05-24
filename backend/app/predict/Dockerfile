FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./backend/app/predict/requirements.txt .

RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install ultralytics --no-deps && \
    pip install -r requirements.txt

COPY ./backend/app ./app

CMD ["celery", "-A", "app.predict.tasks.celery_app", "worker", "--loglevel=info", "--concurrency=1", "--without-gossip", "--without-mingle", "--without-heartbeat"]