from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from app.models.order import Order, OrderItem
from app.models.book import Book
from app.models.discount import Discount
from app.database import get_session
from datetime import date, datetime
from fastapi import HTTPException
from pydantic import BaseModel

class OrderItemRequest(BaseModel):
    book_id: int
    quantity: int

def create_order(user_id: int, items: List[OrderItemRequest], session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Create a new order from the provided items list.

    Args:
        user_id: The ID of the user
        items: List of items with book_id and quantity
        session: Optional database session

    Returns:
        A dictionary containing the created order information

    Raises:
        HTTPException: If the items list is empty, book not found, or quantity is invalid
    """
    if session is None:
        session = get_session()

    if not items:
        raise HTTPException(status_code=400, detail="No items provided")

    # Get current date to check for active discounts
    today = date.today()

    # Get book details for all items
    book_details = {}

    for item in items:
        # Check if book exists
        book_query = select(Book).where(Book.id == item.book_id)
        book = session.exec(book_query).first()

        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {item.book_id} not found")

        # Validate quantity
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

        if item.quantity > 8:
            raise HTTPException(status_code=400, detail="Maximum quantity allowed is 8")

        # Store book details for later use
        book_details[item.book_id] = book

    # Calculate order total and prepare order items
    order_items_data = []
    order_total = 0

    for item in items:
        book = book_details[item.book_id]

        # Check for active discount
        discount_query = (
            select(Discount)
            .where(Discount.book_id == book.id)
            .where(Discount.discount_start_date <= today)
            .where(Discount.discount_end_date >= today)
        )

        discount = session.exec(discount_query).first()

        # Calculate item price
        item_price = discount.discount_price if discount else book.book_price
        item_total = item_price * item.quantity

        # Add to order total
        order_total += item_total

        # Prepare order item data
        order_items_data.append({
            "book_id": item.book_id,
            "quantity": item.quantity,
            "price": item_price
        })

    # Create order
    new_order = Order(
        user_id=user_id,
        order_date=datetime.now(),
        order_amount=order_total
    )

    session.add(new_order)
    session.flush()  # Get the order ID

    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            book_id=item_data["book_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        session.add(order_item)

    session.commit()

    # Format the response
    order_items = []

    for item_data in order_items_data:
        book = book_details[item_data["book_id"]]

        order_items.append({
            "book_id": item_data["book_id"],
            "title": book.book_title,
            "quantity": item_data["quantity"],
            "price": item_data["price"],
            "item_total": item_data["price"] * item_data["quantity"]
        })

    result = {
        "success": True,
        "order": {
            "id": new_order.id,
            "user_id": new_order.user_id,
            "order_date": new_order.order_date,
            "order_amount": new_order.order_amount,
            "items": order_items
        }
    }

    return result

def get_user_orders(user_id: int, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Get all orders for a specific user.

    Args:
        user_id: The ID of the user
        session: Optional database session

    Returns:
        A dictionary containing the list of orders
    """
    if session is None:
        session = get_session()

    # Get all orders for the user
    orders_query = select(Order).where(Order.user_id == user_id).order_by(Order.order_date.desc())
    orders = session.exec(orders_query).all()

    result = []

    for order in orders:
        # Get order items
        order_items_query = (
            select(OrderItem, Book)
            .join(Book, OrderItem.book_id == Book.id)
            .where(OrderItem.order_id == order.id)
        )

        order_items_result = session.exec(order_items_query).all()

        # Format order items
        items = []

        for order_item, book in order_items_result:
            items.append({
                "book_id": order_item.book_id,
                "title": book.book_title,
                "quantity": order_item.quantity,
                "price": order_item.price,
                "item_total": order_item.price * order_item.quantity
            })

        # Format order
        result.append({
            "id": order.id,
            "order_date": order.order_date,
            "order_amount": order.order_amount,
            "items": items
        })

    return {
        "items": result,
        "total": len(result)
    }

def get_order_detail(order_id: int, user_id: int, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific order.

    Args:
        order_id: The ID of the order
        user_id: The ID of the user (for authorization)
        session: Optional database session

    Returns:
        A dictionary containing the order details

    Raises:
        HTTPException: If the order is not found or doesn't belong to the user
    """
    if session is None:
        session = get_session()

    # Get order
    order_query = select(Order).where(Order.id == order_id)
    order = session.exec(order_query).first()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

    # Check if order belongs to user
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    # Get order items
    order_items_query = (
        select(OrderItem, Book)
        .join(Book, OrderItem.book_id == Book.id)
        .where(OrderItem.order_id == order.id)
    )

    order_items_result = session.exec(order_items_query).all()

    # Format order items
    items = []

    for order_item, book in order_items_result:
        items.append({
            "book_id": order_item.book_id,
            "title": book.book_title,
            "cover_photo": book.book_cover_photo,
            "quantity": order_item.quantity,
            "price": order_item.price,
            "item_total": order_item.price * order_item.quantity
        })

    # Format response
    result = {
        "id": order.id,
        "user_id": order.user_id,
        "order_date": order.order_date,
        "order_amount": order.order_amount,
        "items": items
    }

    return result
