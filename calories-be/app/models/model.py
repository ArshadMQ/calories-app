from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.session import Base
from datetime import timezone
import datetime
from sqlalchemy.orm import relationship

UTC = timezone.utc


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    dishes = relationship("Dish", back_populates="users")


class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    servings = Column(String, nullable=False)
    calories_per_serving = Column(String, nullable=False)
    total_calories = Column(String, nullable=False)
    source = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now(UTC))
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(UTC),
        onupdate=datetime.datetime.now(UTC)
    )

    users = relationship("User", back_populates="dishes")
