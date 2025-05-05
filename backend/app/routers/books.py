from fastapi import APIRouter, Query, Depends, Path
from app.services import get_books, get_books_on_sale, get_popular_books, get_recommended_books, get_book_detail
from app.services.book_detail import get_book_detail
from sqlmodel import Session
from typing import Dict, Any, Optional, List
from app.database import get_session

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=Dict[str, Any])
async def get_books_route(
    category_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None, ge=1, le=5, description="Minimum average rating (1-5)"),
    sort_by: Optional[str] = Query(None, description="Options: price_asc, price_desc, discount_desc, popularity_desc"),
    page: int = Query(1, ge=1),
    size: int = Query(15, description="Options: 5, 15, 20, 25"),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get a paginated list of books with filtering and sorting options.

    Supports:
    - Filtering by category, author, and minimum rating
    - Sorting by price (asc/desc), discount (desc), and popularity (desc)
    - Pagination

    Returns a dictionary with total count, page info, and list of books.
    """
    return get_books(
        category_id=category_id,
        author_id=author_id,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        size=size,
        session=session
    )

@router.get("/on-sale", response_model=List[Dict[str, Any]])
async def get_books_on_sale_route(
    limit: int = Query(10, ge=1),
    session: Optional[Session] = Depends(get_session)
) -> List[Dict[str, Any]]:
    return get_books_on_sale(limit=limit, session=session)

@router.get("/popular", response_model=Dict[str, Any])
async def get_popular_books_route(
    limit: int = Query(8, ge=1),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    return get_popular_books(limit=limit, session=session)

@router.get("/recommended", response_model=Dict[str, Any])
async def get_recommended_books_route(
    limit: int = Query(8, ge=1),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    return get_recommended_books(limit=limit, session=session)

@router.get("/{book_id}", response_model=Dict[str, Any])
async def get_book_detail_route(
    book_id: int = Path(..., title="The ID of the book to get", ge=1),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific book.

    This endpoint retrieves comprehensive information about a book including:
    - Basic book details (title, summary, price, etc.)
    - Category information
    - Author information
    - Current discount (if any)
    """
    return get_book_detail(book_id=book_id, session=session)

