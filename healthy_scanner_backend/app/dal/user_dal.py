# app/dal/user_dal.py
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserDal:
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        new_user = User(
            id=str(uuid4()),
            name=user_in.name,
            habits=user_in.habits,
            conditions=user_in.conditions,
            allergies=user_in.allergies,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get(db: Session, user_id: str) -> Optional[User]:
        return (
            db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            db.query(User)
            .filter(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(db: Session, user_id: str, user_in: UserUpdate) -> Optional[User]:
        user = (
            db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        if not user:
            return None

        data = user_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def soft_delete(db: Session, user_id: str) -> bool:
        user = (
            db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        if not user:
            return False

        user.deleted_at = datetime.utcnow()
        db.commit()
        return True
