from typing import Optional, List
from datetime import datetime
from sqlalchemy import BigInteger, Column, Integer, SmallInteger, Numeric, DateTime, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.book import Book

class Order(SQLModel, table=True):
    __tablename__ = "order"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("user.id")))
    order_date: datetime = Field(sa_column=Column("order_date", DateTime(0)))
    order_amount: float = Field(sa_column=Column(Numeric(8, 2)))
    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    order_id: int = Field(sa_column=Column(BigInteger, ForeignKey("order.id")))
    book_id: int = Field(sa_column=Column(BigInteger, ForeignKey("book.id")))
    quantity: int = Field(sa_column=Column(SmallInteger))
    price: float = Field(sa_column=Column(Numeric(5, 2)))
    order: Optional["Order"] = Relationship(back_populates="order_items")
    book: Optional["Book"] = Relationship()
