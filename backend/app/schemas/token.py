from typing import Dict, Any, Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    type: Optional[str] = None
