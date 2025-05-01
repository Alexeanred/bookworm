from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy import func, desc
from app.models.book import Book
from app.models.review import Review
from app.models.discount import Discount
from app.database import get_session
from datetime import date

def get_popular_books(limit: int = 8, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Get top books with most reviews and lowest final price.
    
    Logic:
    1. Count the number of reviews for each book
    2. Sort by number of reviews (descending)
    3. If there are more than 'limit' books, get the ones with lowest final price
    
    Returns a dictionary with total count and list of popular books.
    """
    if session is None:
        session = get_session()
    
    # Get current date to check for active discounts
    today = "2022-10-08"
    
    # Subquery to get the number of reviews and average rating for each book
    reviews_stats_subquery = (
        select(
            Review.book_id,
            func.count(Review.id).label("reviews_count"),
            func.avg(Review.rating_star).label("avg_rating")
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
    
    # Main query to get books with review counts, avg rating, and prices
    query = (
        select(
            Book,
            reviews_stats_subquery.c.reviews_count,
            reviews_stats_subquery.c.avg_rating,
            func.coalesce(discount_subquery.c.discounted_price, Book.book_price).label("final_price")
        )
        .join(reviews_stats_subquery, Book.id == reviews_stats_subquery.c.book_id)
        .outerjoin(discount_subquery, Book.id == discount_subquery.c.book_id)
        .order_by(desc("reviews_count"), "final_price")
        .limit(limit)
    )
    
    # Execute the query
    results = session.exec(query).all()
    
    # Format the results
    formatted_results = []
    for book, reviews_count, avg_rating, final_price in results:
        formatted_results.append({
            'id': book.id,
            'title': book.book_title,
            'summary': book.book_summary,
            'original_price': book.book_price,
            'final_price': final_price,
            'reviews_count': reviews_count,
            'avg_rating': float(avg_rating) if avg_rating is not None else None,
            'cover': book.book_cover_photo,
            'category_id': book.category_id,
            'author_id': book.author_id,
            'author_name': book.author.author_name if book.author else None,
        })
    
    return {
        'total': len(formatted_results),
        'items': formatted_results
    }
