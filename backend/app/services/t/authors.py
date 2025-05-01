from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy import func
from app.models.author import Author
from app.models.book import Book
from app.database import get_session

def get_authors(session: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Get all authors with book count for each author.
    
    Args:
        session: Optional database session
        
    Returns:
        A list of dictionaries containing author information
    """
    if session is None:
        session = get_session()
    
    # Query to get all authors
    authors_query = select(Author)
    authors = session.exec(authors_query).all()
    
    # Format the results and count books for each author
    result = []
    for author in authors:
        # Count books by this author
        book_count_query = select(func.count(Book.id)).where(Book.author_id == author.id)
        book_count = session.exec(book_count_query).one()
        
        result.append({
            'id': author.id,
            'name': author.author_name,
            'bio': author.author_bio,
            'book_count': book_count or 0
        })
    
    return result
