from typing import Optional, List
from sqlalchemy import BigInteger, Column
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.book import Book

class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    category_name: str = Field(max_length=120)
    category_desc: Optional[str] = Field(default=None, max_length=255)
    # 1 category has many books
    books: List["Book"] = Relationship(back_populates="category")

