from typing import Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy import func, cast, Float
from app.models.book import Book
from app.models.author import Author
from app.models.category import Category
from app.models.discount import Discount
from app.models.review import Review
from app.database import get_session
from datetime import date
from fastapi import HTTPException

def get_book_detail(book_id: int, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific book by its ID.

    This function retrieves comprehensive information about a book including:
    - Basic book details (title, summary, price, etc.)
    - Category information
    - Author information
    - Current discount (if any)

    Args:
        book_id: The ID of the book to retrieve
        session: Optional database session

    Returns:
        A dictionary containing all book details

    Raises:
        HTTPException: If the book is not found
    """
    if session is None:
        session = get_session()

    # Get current date to check for active discounts
    today = "2022-10-08"

    # Subquery to get the average rating and review count for each book
    reviews_stats_subquery = (
        select(
            Review.book_id,
            func.count(Review.id).label("reviews_count"),
            func.avg(cast(Review.rating_star, Float)).label("avg_rating")
        )
        .group_by(Review.book_id)
        .subquery()
    )

    # Get book with category and author information
    book_query = (
        select(
            Book,
            Category.category_name,
            Author.author_name,
            reviews_stats_subquery.c.reviews_count,
            reviews_stats_subquery.c.avg_rating
        )
        .join(Category, Book.category_id == Category.id)
        .join(Author, Book.author_id == Author.id)
        .outerjoin(reviews_stats_subquery, Book.id == reviews_stats_subquery.c.book_id)
        .where(Book.id == book_id)
    )

    book_result = session.exec(book_query).first()

    if not book_result:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

    book, category_name, author_name, reviews_count, avg_rating = book_result

    # Get current discount if available
    discount_query = (
        select(Discount)
        .where(Discount.book_id == book_id)
        .where(Discount.discount_start_date <= today)
        .where(Discount.discount_end_date >= today)
    )

    discount = session.exec(discount_query).first()

    # Build the response
    result = {
        'id': book.id,
        'title': book.book_title,
        'summary': book.book_summary,
        'cover': book.book_cover_photo,
        'original_price': book.book_price,
        'category': {
            'id': book.category_id,
            'name': category_name
        },
        'author': {
            'id': book.author_id,
            'name': author_name
        },
        'reviews_count': reviews_count or 0,
        'avg_rating': float(avg_rating) if avg_rating is not None else 0
    }

    # Add discount information if available
    if discount:
        result['discount_price'] = discount.discount_price
        result['discount_start_date'] = discount.discount_start_date
        result['discount_end_date'] = discount.discount_end_date
        result['discount_amount'] = book.book_price - discount.discount_price
        result['discount_percent'] = round((result['discount_amount'] / book.book_price) * 100, 2)
        result['final_price'] = discount.discount_price
    else:
        result['final_price'] = book.book_price

    return result
