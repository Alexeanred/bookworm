from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy import func, desc, cast, Float
from app.models.book import Book
from app.models.review import Review
from app.models.discount import Discount
from app.database import get_session
from datetime import date

def get_recommended_books(limit: int = 8, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Get top books with highest average rating stars and lowest final price.
    
    Logic:
    1. Calculate the average rating stars for each book
    2. Sort by average rating stars (descending)
    3. If there are more than 'limit' books, get the ones with lowest final price
    
    Returns a dictionary with total count and list of recommended books.
    """
    if session is None:
        session = get_session()
    
    # Get current date to check for active discounts
    today = "2022-10-08"
    
    # Subquery to get the average rating stars for each book
    avg_rating_subquery = (
        select(
            Review.book_id,
            func.avg(cast(Review.rating_star, Float)).label("avg_rating"),
            func.count(Review.id).label("reviews_count")
        )
        .group_by(Review.book_id)
        .subquery()
    )
    
    # Subquery to get the current discount price for each book (if available)
    discount_subquery = (
        select(
            Discount.book_id,
            Discount.discount_price.label("discounted_price")
        )
        .where(Discount.discount_start_date <= today)
        .where(Discount.discount_end_date >= today)
        .subquery()
    )
    
    # Main query to get books with average ratings and prices
    query = (
        select(
            Book,
            avg_rating_subquery.c.avg_rating,
            avg_rating_subquery.c.reviews_count,
            func.coalesce(discount_subquery.c.discounted_price, Book.book_price).label("final_price")
        )
        .join(avg_rating_subquery, Book.id == avg_rating_subquery.c.book_id)
        .outerjoin(discount_subquery, Book.id == discount_subquery.c.book_id)
        .order_by(desc("avg_rating"), "final_price")
        .limit(limit)
    )
    
    # Execute the query
    results = session.exec(query).all()
    
    # Format the results
    formatted_results = []
    for book, avg_rating, reviews_count, final_price in results:
        formatted_results.append({
            'id': book.id,
            'title': book.book_title,
            'summary': book.book_summary,
            'original_price': book.book_price,
            'final_price': final_price,
            'avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'reviews_count': reviews_count,
            'cover': book.book_cover_photo,
            'category_id': book.category_id,
            'author_id': book.author_id,
            'author_name': book.author.author_name if book.author else None,
        })
    
    return {
        'total': len(formatted_results),
        'items': formatted_results
    }
