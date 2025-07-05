from dns.e164 import query
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.calories import CalorieRequest, CalorieResponse
from app.services.usda import fetch_calories
from fastapi.security import OAuth2PasswordBearer
import jwt, os
from sqlalchemy import DateTime
from sqlalchemy.orm import Session
from app.models.model import User, Dish
from app.utils.base import current_user, get_timezone_from_offset, days_ago
from app.db.session import db_session_connection
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone

load_dotenv()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


@router.post("/get-calories", response_model=CalorieResponse)
async def get_calories(data: CalorieRequest,
                       user: User = Depends(current_user),
                       db_session: Session = Depends(db_session_connection)):
    if (isinstance(user, dict) and user.get("status_code") == status.HTTP_401_UNAUTHORIZED):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User")

    if not data.dish_name:
        raise HTTPException(status_code=400, detail="Input dish name")

    if not data.servings or data.servings <= 0:
        raise HTTPException(status_code=400, detail="Input servings")

    name, cal = await fetch_calories(data.dish_name)
    if cal == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    total = cal * data.servings
    dish = Dish(name=name, servings=data.servings, calories_per_serving=cal,
                source="USDA FoodData Central", total_calories=total, user_id=user.id)
    db_session.add(dish)
    db_session.commit()
    return CalorieResponse(
        dish_name=name,
        servings=data.servings,
        calories_per_serving=cal,
        total_calories=total,
        source="USDA FoodData Central",
        created_at=str(datetime.utcnow()),
        updated_at=str(datetime.utcnow()),
    )


@router.get("/list-dishes", response_model=List[CalorieResponse])
async def list_dishes(
        user: User = Depends(current_user),
        db_session: Session = Depends(db_session_connection)):
    if (isinstance(user, dict) and user.get("status_code") == status.HTTP_401_UNAUTHORIZED):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User")

    dish = db_session.query(Dish).filter(Dish.user_id == user.id).all()
    return [
        CalorieResponse(
            dish_name=d.name,
            servings=d.servings,
            calories_per_serving=d.calories_per_serving,
            total_calories=d.total_calories,
            source=d.source,
            created_at=str(d.created_at),
            updated_at=str(d.updated_at)
        )
        for d in dish
    ]
