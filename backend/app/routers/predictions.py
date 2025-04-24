from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user, User, Session, get_session

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Mock function to return fake prediction history
def get_all_image_metadata_by_user(session, user_id):
    return [
        {
            "image_id": "mock_image_id_1",
            "minio_url": "https://mock-minio-url/1.jpg",
            "object_key": f"{user_id}/1.jpg",
            "uploaded_at": "2025-04-24T12:00:00Z",
            "binary_mask": [[0, 1], [1, 0]],
            "cdf_data": [0.1, 0.9]
        },
        {
            "image_id": "mock_image_id_2",
            "minio_url": "https://mock-minio-url/2.jpg",
            "object_key": f"{user_id}/2.jpg",
            "uploaded_at": "2025-04-24T12:05:00Z",
            "binary_mask": [[1, 0], [0, 1]],
            "cdf_data": [0.2, 0.8]
        }
    ]

@router.get("/", response_model=list[dict])
async def get_predictions(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Return mock prediction history for the authenticated user
    return get_all_image_metadata_by_user(session, user.user_id)