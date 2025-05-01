from typing import Optional, List
from sqlalchemy import BigInteger, Column, Text
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.book import Book

class Author(SQLModel, table=True):
    __tablename__ = "author"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    author_name: str = Field(max_length=255)
    author_bio: Optional[str] = Field(default=None, sa_column=Column(Text))
    # 1 author has many books
    books: List["Book"] = Relationship(back_populates="author")
