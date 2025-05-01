from typing import Optional
from datetime import date
from sqlalchemy import BigInteger, Column, Numeric, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.book import Book

class Discount(SQLModel, table=True):
    __tablename__ = "discount"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    book_id: int = Field(sa_column=Column(BigInteger, ForeignKey("book.id")))
    discount_start_date: date
    discount_end_date: Optional[date] = None
    discount_price: float = Field(sa_column=Column(Numeric(5, 2)))
    book: Optional["Book"] = Relationship(back_populates="discounts")
