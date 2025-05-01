from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, Boolean, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    user_id: int = Field(sa_column=Column(BigInteger, ForeignKey("user.id")))
    token: str = Field(max_length=255)
    expires_at: datetime = Field(sa_column=Column(DateTime(0)))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(0)))
    is_revoked: bool = Field(default=False, sa_column=Column(Boolean))
    user_agent: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)

    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
