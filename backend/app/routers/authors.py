from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Dict, Any, Optional, List
from app.database import get_session
from app.services import get_authors

router = APIRouter(prefix="/authors", tags=["Authors"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_authors_route(
    session: Optional[Session] = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Get all authors with book count for each author.
    
    Returns a list of authors with their ID, name, bio, and the number of books by each author.
    """
    return get_authors(session=session)
