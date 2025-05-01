from typing import Optional
from datetime import datetime
from sqlalchemy import BigInteger, Column, Text, DateTime, SmallInteger, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.book import Book

class Review(SQLModel, table=True):
    __tablename__ = "review"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    book_id: int = Field(sa_column=Column(BigInteger, ForeignKey("book.id")))
    review_title: str = Field(max_length=120)
    review_details: Optional[str] = Field(default=None, sa_column=Column(Text))
    review_date: datetime = Field(sa_column=Column("review_date", DateTime(0)))
    rating_star: int = Field(sa_column=Column(SmallInteger))
    book: Optional["Book"] = Relationship(back_populates="reviews")
