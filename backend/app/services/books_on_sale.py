from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy import func, desc, cast, Float
from datetime import date
from app.models.book import Book
from app.models.discount import Discount
from app.models.review import Review
from app.database import get_session

def get_books_on_sale(limit: int = 10, session: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Get top books with the most discount.
    Formula: discount_amount = book_price - discount_price
    Returns top books sorted by discount_amount in descending order.
    """
    if session is None:
        session = get_session()

    # Get current date to filter active discounts
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

    # Create a query that joins Book and Discount tables
    # and calculates the discount amount
    query = (
        select(
            Book,
            Discount,
            (Book.book_price - Discount.discount_price).label("discount_amount"),
            reviews_stats_subquery.c.reviews_count,
            reviews_stats_subquery.c.avg_rating
        )
        .join(Discount, Book.id == Discount.book_id)
        .outerjoin(reviews_stats_subquery, Book.id == reviews_stats_subquery.c.book_id)
        .where(Discount.discount_start_date <= today)
        .where(Discount.discount_end_date >= today)
        .order_by(desc("discount_amount"))
        .limit(limit)
    )

    # Execute the query
    results = session.exec(query).all()

    # Format the results
    formatted_results = []
    for book, discount, discount_amount, reviews_count, avg_rating in results:
        formatted_results.append({
            'id': book.id,
            'title': book.book_title,
            'summary': book.book_summary,
            'original_price': book.book_price,
            'discount_price': discount.discount_price,
            'discount_amount': discount_amount,
            'discount_percent': round((discount_amount / book.book_price) * 100, 2),
            'cover': book.book_cover_photo,
            'category_id': book.category_id,
            'author_id': book.author_id,
            'author_name': book.author.author_name if book.author else None,
            'discount_start_date': discount.discount_start_date,
            'discount_end_date': discount.discount_end_date,
            'reviews_count': reviews_count or 0,
            'avg_rating': float(avg_rating) if avg_rating is not None else 0
        })

    return formatted_results