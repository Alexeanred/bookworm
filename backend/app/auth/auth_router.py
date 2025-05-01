from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import (
    create_access_token, 
    create_refresh_token, 
    verify_token,
    get_user_id_from_token,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from app.auth.auth_service import (
    authenticate_user, 
    get_user_by_email,
    create_refresh_token_in_db,
    get_refresh_token,
    revoke_token,
    revoke_all_user_tokens
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Login endpoint to get access token and refresh token
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in database
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    user_agent = request.headers.get("user-agent")
    client_host = request.client.host if request.client else None
    
    create_refresh_token_in_db(
        session=session,
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=client_host
    )
    
    # Set refresh token in HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60*60*24*REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    # Return access token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "admin": user.admin
        }
    }

@router.post("/refresh")
async def refresh_token_endpoint(
    response: Response,
    request: Request,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token from cookie
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token in database
    db_token = get_refresh_token(session, refresh_token)
    if not db_token:
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify JWT
    try:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = int(payload.get("sub"))
        if user_id != db_token.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token mismatch",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Return new access token
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "admin": user.admin
            }
        }
    
    except:
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Logout endpoint to revoke refresh token
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        revoke_token(session, refresh_token)
    
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all(
    response: Response,
    token: str = Depends(JWTBearer()),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Logout from all devices by revoking all refresh tokens
    """
    user_id = get_user_id_from_token(token)
    revoke_all_user_tokens(session, user_id)
    
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out from all devices"}

@router.get("/me")
async def get_current_user(
    token: str = Depends(JWTBearer()),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get current user information
    """
    user_id = get_user_id_from_token(token)
    user = session.get(User, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "admin": user.admin
    }
