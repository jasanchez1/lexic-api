from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.token import Token


def create_token(
    db: Session, 
    user_id: UUID,
    token: str,
    token_type: str,
    expires_at: datetime
) -> Token:
    """
    Create a new token in the database
    """
    db_token = Token(
        user_id=user_id,
        token=token,
        type=token_type,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_token_by_token(db: Session, token: str) -> Optional[Token]:
    """
    Get a token by its value
    """
    return db.query(Token).filter(Token.token == token).first()


def get_token_by_jti(db: Session, jti: str) -> Optional[Token]:
    """
    Get a token by JTI
    """
    return db.query(Token).filter(Token.token == jti).first()


def revoke_token(db: Session, token: Token) -> Token:
    """
    Revoke a token
    """
    token.is_revoked = True
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def delete_expired_tokens(db: Session) -> int:
    """
    Delete all expired tokens
    """
    result = db.query(Token).filter(Token.expires_at < datetime.now(timezone.utc)).delete()
    db.commit()
    return result