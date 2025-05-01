from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy import func
from app.models.category import Category
from app.models.book import Book
from app.database import get_session

def get_categories(session: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Get all categories with book count for each category.

    Args:
        session: Optional database session

    Returns:
        A list of dictionaries containing category information
    """
    if session is None:
        session = get_session()

    # Query to get all categories ordered by category_name
    categories_query = select(Category).order_by(Category.category_name)
    categories = session.exec(categories_query).all()

    # Format the results and count books in each category
    result = []
    for category in categories:
        # Count books in this category
        book_count_query = select(func.count(Book.id)).where(Book.category_id == category.id)
        book_count = session.exec(book_count_query).one()

        result.append({
            'id': category.id,
            'name': category.category_name,
            'description': category.category_desc,
            'book_count': book_count or 0
        })

    return result
