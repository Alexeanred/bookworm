from typing import Optional, List
from sqlalchemy import BigInteger, Column, Text, Numeric, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.author import Author
    from app.models.review import Review
    from app.models.discount import Discount
    from app.models.order import OrderItem

class Book(SQLModel, table=True):
    __tablename__ = "book"
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    category_id: int = Field(sa_column=Column(BigInteger, ForeignKey("category.id")))
    author_id: int = Field(sa_column=Column(BigInteger, ForeignKey("author.id")))
    book_title: str = Field(max_length=255)
    book_summary: str = Field(sa_column=Column(Text))
    book_price: float = Field(sa_column=Column(Numeric(5, 2)))
    book_cover_photo: Optional[str] = Field(default=None, max_length=20)

    category: Optional["Category"] = Relationship(back_populates="books")
    author: Optional["Author"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book")
    discounts: List["Discount"] = Relationship(back_populates="book")
    order_items: List["OrderItem"] = Relationship(back_populates="book")
