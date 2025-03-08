from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    sub: str  # subject (user ID)
    exp: int  # expiration time
    type: str = "access"  # token type
    jti: Optional[str] = None  # JWT ID (for refresh tokens)