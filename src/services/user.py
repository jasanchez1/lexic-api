from sqlalchemy.orm import Session
from core.security import get_password_hash, verify_password
from models.user import User
from schemas.user import UserCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: UserCreate) -> User:
        db_user = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=get_password_hash(user.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user