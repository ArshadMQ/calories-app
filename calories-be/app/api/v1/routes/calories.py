from fastapi import APIRouter, Depends, HTTPException
from app.schemas.calories import CalorieRequest, CalorieResponse
from app.services.usda import fetch_calories
from fastapi.security import OAuth2PasswordBearer
import jwt, os
from app.models.user import User
from app.utils.base import current_user

from dotenv import load_dotenv

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
                       user: User = Depends(current_user)):
    if data.servings <= 0:
        raise HTTPException(status_code=400, detail="Invalid servings")

    name, cal = await fetch_calories(data.dish_name)
    if cal == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    total = cal * data.servings
    return CalorieResponse(
        dish_name=name,
        servings=data.servings,
        calories_per_serving=cal,
        total_calories=total,
        source="USDA FoodData Central"
    )
