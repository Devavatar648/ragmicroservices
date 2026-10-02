from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    def __init__(self, db:Session):
        self.db = db

    def create_user(self, user:User)->User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user;

    def get_user_by_email(self, email:str)->User | None:
        statement = select(User).where(
            User.email==email
        )

        return self.db.scalar(statement)
    
    def get_user_by_userId(self, user_id:str)->User | None:
        statement = select(User).where(
            User.id==user_id
        )

        return self.db.scalar(statement)
    
    def get_all_users(self)->list[User]:
        statement = select(User).order_by(
            User.created_at.desc()
        )

        return list(self.db.scalars(statement).all())
    
    def update_user(self, db_user: User, update_data: dict) -> User | None:
        # Apply updates dynamically from a plain dictionary
        for key, value in update_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user
   
    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
