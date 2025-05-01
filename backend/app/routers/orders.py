from fastapi import APIRouter, Depends, Path
from sqlmodel import Session
from typing import Dict, Any, Optional, List
from app.database import get_session
from app.services.order import create_order, get_user_orders, get_order_detail, OrderItemRequest
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import get_user_id_from_token

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=Dict[str, Any])
async def create_order_route(
    items: List[OrderItemRequest],
    token: str = Depends(JWTBearer()),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    """
    Create a new order from the provided items list.

    This endpoint:
    1. Validates the provided items (checks if books exist and quantities are valid)
    2. Creates a new order with the provided items
    3. Returns the created order information

    Note: All books are assumed to be in stock.

    Authentication required: This endpoint requires a valid JWT token.
    """
    user_id = get_user_id_from_token(token)
    result = create_order(user_id=user_id, items=items, session=session)
    return result

@router.get("/", response_model=Dict[str, Any])
async def get_orders_route(
    token: str = Depends(JWTBearer()),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get all orders for the authenticated user.

    Returns a list of orders with basic information.

    Authentication required: This endpoint requires a valid JWT token.
    """
    user_id = get_user_id_from_token(token)
    return get_user_orders(user_id=user_id, session=session)

@router.get("/{order_id}", response_model=Dict[str, Any])
async def get_order_detail_route(
    order_id: int = Path(..., title="The ID of the order to get", ge=1),
    token: str = Depends(JWTBearer()),
    session: Optional[Session] = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific order.

    This endpoint retrieves comprehensive information about an order including:
    - Basic order details (ID, date, total amount)
    - All items in the order with their details

    Note: This endpoint only allows users to view their own orders.

    Authentication required: This endpoint requires a valid JWT token.
    """
    user_id = get_user_id_from_token(token)
    return get_order_detail(order_id=order_id, user_id=user_id, session=session)
