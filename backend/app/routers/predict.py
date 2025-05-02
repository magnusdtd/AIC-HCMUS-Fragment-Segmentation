from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.models.database import get_session, Prediction
from app.routers.auth import get_current_user
from app.models.queries import get_user_by_username, create_img_metadata, create_prediction, fetch_prediction_from_minio
from app.utils.model import model
from sqlmodel import Session
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
from app.models.queries import create_prediction
import base64, io
from torchvision.utils import draw_segmentation_masks
import torch
import numpy as np

router = APIRouter()

@router.post("/upload")
async def upload_image(
    file: UploadFile, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        username = current_user["user"]
        user = get_user_by_username(db, username)

        metadata = await create_img_metadata(db, user, file)

        return {"message": "File uploaded successfully", "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_predict")
async def upload_and_predict(
    file: UploadFile, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        # Get the current user
        username = current_user["user"]
        user = get_user_by_username(db, username)

        # Store metadata in the database
        metadata = await create_img_metadata(db, user, file)

        # Process the uploaded image
        image = await _read_and_convert_image(file)

        # Perform prediction using the model
        binary_masks, volumes, is_calibrated = await model.predict(image, conf=0.5, iou=0.5)

        # Convert volumes (NumPy array) to a list
        volumes_list = volumes.tolist() if isinstance(volumes, np.ndarray) else volumes

        # Overlay segmentation masks on the image
        overlaid_image_base64 = _generate_overlaid_image(image, binary_masks)

        # Store prediction in the database
        await create_prediction(db, metadata.id, binary_masks, volumes_list, is_calibrated)

        return {
            "message": "Prediction completed successfully",
            "metadata": metadata,
            "volumes": volumes_list,
            "overlaid_image": overlaid_image_base64,
            "is_calibrated": is_calibrated 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _read_and_convert_image(file: UploadFile) -> Image.Image:
    """Read the uploaded file and convert it to a Pillow image."""
    file_content = await file.read()
    return Image.open(io.BytesIO(file_content)).convert("RGBA")


def _generate_overlaid_image(image: Image.Image, binary_masks: list) -> str:
    """Generate an overlaid image with segmentation masks and return it as a base64 string."""
    # Convert the image to a PyTorch tensor
    image_tensor = torch.tensor(
        list(image.getdata()), dtype=torch.uint8
    ).reshape(image.size[1], image.size[0], 4).permute(2, 0, 1)

    # Resize binary masks to match the image dimensions
    resized_masks = [
        torch.tensor(
            np.array(Image.fromarray(mask.astype(np.uint8)).resize(image.size, Image.NEAREST)),
            dtype=torch.bool
        )
        for mask in binary_masks
    ]
    masks_tensor = torch.stack(resized_masks)

    # Generate random colors for each mask
    num_masks = masks_tensor.shape[0]
    colors = torch.randint(0, 256, (num_masks, 3), dtype=torch.uint8)

    # Draw segmentation masks on the image tensor
    overlaid_image_tensor = draw_segmentation_masks(
        image_tensor[:3], 
        masks_tensor,
        alpha=0.5,
        colors=colors.tolist()
    )

    # Convert the overlaid image tensor back to a Pillow image
    overlaid_image = Image.fromarray(overlaid_image_tensor.permute(1, 2, 0).numpy(), mode="RGB")

    # Convert the overlaid image to base64
    buffer = BytesIO()
    overlaid_image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

  
@router.get("/fetch_prediction")
def fetch_prediction(
    img_id: int,
    upload_time: datetime,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
    try:
        # Query the prediction from the database
        prediction = db.query(Prediction).filter(
            Prediction.id == img_id,
            Prediction.update_time == upload_time
        ).first()

        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")

        # Fetch binary masks and volumes from MinIO
        binary_masks, volumes = fetch_prediction_from_minio(
            prediction.binary_mask_key, 
            prediction.volumes_key
        )

        return {
            "binary_masks": binary_masks,
            "volumes": volumes,
            "is_calibrated": prediction.has_calibrated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("re_predict")
def get_prediction(
    img_name: str,
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
  # User want to re-predict their image. Store new prediction to database.
  try:
      pass
  except Exception as e:
      raise Exception(status_code=500, detail=str(e))
  
@router.get("get_prediction_metadata")
def get_prediction_metadata(
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)  
):
  # The frontend will show user all of their images and predictions
  # For each image of an user, server will return all of their prediction .
  # (img_id, update_time)
  try:
      pass
  except Exception as e:
      raise Exception(status_code=500, detail=str(e))
