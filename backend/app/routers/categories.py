from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Dict, Any, Optional, List
from app.database import get_session
from app.services import get_categories

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_categories_route(
    session: Optional[Session] = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Get all categories with book count for each category.
    
    Returns a list of categories with their ID, name, description, and the number of books in each category.
    """
    return get_categories(session=session)
