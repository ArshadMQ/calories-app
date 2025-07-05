from pydantic import Field

from pydantic import BaseModel


class CalorieRequest(BaseModel):
    dish_name: str = None
    servings: int = None


class CalorieResponse(BaseModel):
    dish_name: str
    servings: int
    calories_per_serving: float
    total_calories: float
    source: str
    created_at: str
    updated_at: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    status_code: int
