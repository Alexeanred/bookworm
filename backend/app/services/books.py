from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from sqlalchemy import func, desc, cast, Float
from app.models.book import Book
from app.models.review import Review
from app.models.discount import Discount
from app.models.author import Author
from app.models.category import Category
from app.database import get_session
from datetime import date

PAGE_SIZES = [5, 15, 20, 25]

def get_books(
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    session: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Fetch paginated list of books with advanced filtering and sorting.

    Supports:
    - Filtering by category, author, and minimum rating
    - Sorting by price (asc/desc), discount (desc), and popularity (desc)
    - Pagination

    Args:
        category_id: Optional filter by category ID
        author_id: Optional filter by author ID
        min_rating: Optional filter by minimum average rating (1-5)
        sort_by: Optional sorting method (price_asc, price_desc, discount_desc, popularity_desc)
        page: Page number (starting from 1)
        size: Number of items per page
        session: Optional database session

    Returns:
        Dictionary with total count, page info, and list of books
    """
    if size not in PAGE_SIZES:
        size = 10
    if page < 1:
        page = 1
    if session is None:
        session = get_session()

    # Get current date to check for active discounts
    today = "2022-10-08"  # Using a fixed date for now

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

    # Subquery to get the current discount price for each book (if available)
    discount_subquery = (
        select(
            Discount.book_id,
            Discount.discount_price.label("discount_price"),
            (Book.book_price - Discount.discount_price).label("discount_amount")
        )
        .join(Book, Discount.book_id == Book.id)
        .where(Discount.discount_start_date <= today)
        .where(Discount.discount_end_date >= today)
        .subquery()
    )

    # Main query with all necessary joins
    query = (
        select(
            Book,
            Author,
            Category,
            reviews_stats_subquery.c.reviews_count,
            reviews_stats_subquery.c.avg_rating,
            discount_subquery.c.discount_price,
            discount_subquery.c.discount_amount,
            func.coalesce(discount_subquery.c.discount_price, Book.book_price).label("final_price")
        )
        .join(Author, Book.author_id == Author.id)
        .join(Category, Book.category_id == Category.id)
        .outerjoin(reviews_stats_subquery, Book.id == reviews_stats_subquery.c.book_id)
        .outerjoin(discount_subquery, Book.id == discount_subquery.c.book_id)
    )

    # Apply filters
    if category_id:
        query = query.where(Book.category_id == category_id)
    if author_id:
        query = query.where(Book.author_id == author_id)
    if min_rating:
        # Chỉ hiển thị sách có đánh giá khi áp dụng bộ lọc min_rating
        query = query.where(reviews_stats_subquery.c.avg_rating >= min_rating)

    # Apply sorting
    if sort_by == 'price_asc':
        query = query.order_by("final_price")
    elif sort_by == 'price_desc':
        query = query.order_by(desc("final_price"))
    elif sort_by == 'discount_desc':
        # Sort by discount amount (desc) and then by final price (asc)
        query = query.order_by(
            desc(func.coalesce(discount_subquery.c.discount_amount, 0)),
            "final_price"
        )
    elif sort_by == 'popularity_desc':
        # Sort by review count (desc) and then by final price (asc)
        # Chỉ hiển thị sách có đánh giá khi sắp xếp theo popularity
        query = query.where(reviews_stats_subquery.c.avg_rating > 0)
        query = query.order_by(
            desc(func.coalesce(reviews_stats_subquery.c.reviews_count, 0)),
            "final_price"
        )
    else:
        # Default sorting by ID
        query = query.order_by(Book.id.desc())

    # Create a count query with the same filters
    count_query = (
        select(func.count(Book.id))
        .join(Author, Book.author_id == Author.id)
        .join(Category, Book.category_id == Category.id)
        .outerjoin(reviews_stats_subquery, Book.id == reviews_stats_subquery.c.book_id)
        .outerjoin(discount_subquery, Book.id == discount_subquery.c.book_id)
    )

    # Apply the same filters to the count query
    if category_id:
        count_query = count_query.where(Book.category_id == category_id)
    if author_id:
        count_query = count_query.where(Book.author_id == author_id)
    if min_rating:
        # Cập nhật count query để khớp với query chính
        count_query = count_query.where(reviews_stats_subquery.c.avg_rating >= min_rating)

    # Get total count
    total = session.exec(count_query).one()

    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    results = session.exec(query).all()

    # Format results
    formatted_results = []
    for book, author, category, reviews_count, avg_rating, discount_price, discount_amount, final_price in results:
        formatted_results.append({
            'id': book.id,
            'title': book.book_title,
            'summary': book.book_summary,
            'original_price': book.book_price,
            'discount_price': discount_price,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'cover': book.book_cover_photo,
            'category_id': book.category_id,
            'category_name': category.category_name,
            'author_id': book.author_id,
            'author_name': author.author_name,
            'reviews_count': reviews_count or 0,
            'avg_rating': float(avg_rating) if avg_rating is not None else 0,
        })

    return {
        'total': total,
        'page': page,
        'size': size,
        'items': formatted_results
    }


