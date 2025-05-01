from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Session, select

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.auth.password import verify_password

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get a user by email
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password
    """
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_refresh_token_in_db(
    session: Session, 
    user_id: int, 
    token: str, 
    expires_at: datetime,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> RefreshToken:
    """
    Store a refresh token in the database
    """
    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        is_revoked=False,
        user_agent=user_agent,
        ip_address=ip_address
    )
    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    return db_token

def get_refresh_token(session: Session, token: str) -> Optional[RefreshToken]:
    """
    Get a refresh token from the database
    """
    statement = select(RefreshToken).where(
        RefreshToken.token == token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    )
    return session.exec(statement).first()

def revoke_token(session: Session, token: str) -> bool:
    """
    Revoke a refresh token
    """
    db_token = get_refresh_token(session, token)
    if not db_token:
        return False
    
    db_token.is_revoked = True
    session.add(db_token)
    session.commit()
    return True

def revoke_all_user_tokens(session: Session, user_id: int) -> bool:
    """
    Revoke all refresh tokens for a user
    """
    statement = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    )
    tokens = session.exec(statement).all()
    
    for token in tokens:
        token.is_revoked = True
        session.add(token)
    
    session.commit()
    return True
