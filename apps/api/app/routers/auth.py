from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from apps.api.app.dependencies.db import get_db_session
from cinerec.core.security import verify_google_token, create_access_token
from cinerec.application.user_service import UserService

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login/google", response_model=TokenResponse)
async def login_google(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    idinfo = verify_google_token(request.id_token)
    if not idinfo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    
    # Check if the token was issued for our client
    # The verify_oauth2_token function already does this, but just to be sure
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise HTTPException(status_code=401, detail="Wrong issuer")

    google_id = idinfo["sub"]
    email = idinfo.get("email")
    name = idinfo.get("name", "User")
    picture = idinfo.get("picture")

    user_service = UserService(db)
    user = await user_service.get_user_by_google_id(google_id)
    
    if not user:
        user = await user_service.create_user_from_google(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )

    # Generate our JWT token
    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token)
