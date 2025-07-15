from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from app.models.database import get_session, User
from app.utils.security import manager
from sqlmodel import Session, select
import os
from app.utils.security import RedisSessionStorage
import secrets

router = APIRouter()

# Google OAuth2 config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL")

config_data = {
    'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
    'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET,
    'SECRET_KEY': os.getenv("SECRET_KEY") or ""
}
config = Config(environ={k: v or "" for k, v in config_data.items()})
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
    if not hasattr(oauth, "google") or oauth.google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client is not configured properly.")
    # Generate a random state and store it in Redis using session cookie as key
    state = secrets.token_urlsafe(32)
    session_id = request.session.get('session', None)
    if not session_id:
        # Generate a session id if not present
        session_id = secrets.token_urlsafe(32)
        request.session['session'] = session_id
    redis_store = RedisSessionStorage()
    redis_store.set(f"oauth_state:{session_id}", state, ex=600)
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)

@router.get('/google-callback')
async def google_callback(request: Request, db: Session = Depends(get_session)):
    try:
        if not hasattr(oauth, "google") or oauth.google is None:
            raise HTTPException(status_code=500, detail="Google OAuth client is not configured properly.")
        
        # Retrieve state from request and Redis
        state_from_google = request.query_params.get('state')
        session_id = request.session.get('session', None)
        if not session_id:
            raise HTTPException(status_code=400, detail="Session missing for OAuth state validation.")
        redis_store = RedisSessionStorage()
        state_in_redis = redis_store.get(f"oauth_state:{session_id}")
        if not state_in_redis or state_from_google != state_in_redis:
            raise HTTPException(status_code=400, detail="Google OAuth error: mismatching_state")
        
        # Clean up state
        redis_store.delete(f"oauth_state:{session_id}")
        token = await oauth.google.authorize_access_token(request)
        if not token:
            raise HTTPException(status_code=400, detail="Failed to obtain token from Google.")
        if 'id_token' in token:
            try:
                user_info = await oauth.google.parse_id_token(request, token['id_token'])
            except Exception as e:
                print("parse_id_token error:", e)
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
            password=None
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
