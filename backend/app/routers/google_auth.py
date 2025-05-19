from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request as StarletteRequest
from app.models.database import get_session, User
from app.utils.security import manager
from sqlmodel import Session, select
import os

router = APIRouter()

# Google OAuth2 config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL")

config_data = {
    'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
    'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET,
    'SECRET_KEY': os.getenv("SECRET_KEY")
}
config = Config(environ=config_data)
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get('/google-login')
async def google_login(request: Request):
    redirect_uri = f"{BASE_URL}/api/auth/google-callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/google-callback')
async def google_callback(request: Request, db: Session = Depends(get_session)):
    try:
        token = await oauth.google.authorize_access_token(request)
        if 'id_token' in token:
            try:
                # Try passing just the id_token string
                user_info = await oauth.google.parse_id_token(request, token['id_token'])
            except Exception as e:
                print("parse_id_token error:", e)
                # fallback: fetch userinfo from Google
                user_info = await oauth.google.userinfo(token=token)
        else:
            print("No id_token, fetching userinfo")
            user_info = await oauth.google.userinfo(token=token)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {e.error}")

    # Find or create user
    statement = select(User).where(User.google_id == user_info['sub'])
    user = db.exec(statement).first()
    if not user:
        user = User(
            username=user_info['email'],
            google_id=user_info['sub'],
            email=user_info['email'],
            full_name=user_info.get('name'),
            profile_picture=user_info.get('picture'),
            password='google_oauth'
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = manager.create_access_token(
        data={"sub": user.username}
    )
    # Redirect to frontend with token as query param
    frontend_url = os.getenv("BASE_URL")
    return RedirectResponse(f"{frontend_url}/login?token={access_token}")
