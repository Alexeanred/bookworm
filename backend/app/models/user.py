from typing import Optional, List
from sqlalchemy import BigInteger, Column, Boolean
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.refresh_token import RefreshToken

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=70)
    password: str = Field(max_length=255)
    admin: bool = Field(default=False, sa_column=Column(Boolean))
    orders: List["Order"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
