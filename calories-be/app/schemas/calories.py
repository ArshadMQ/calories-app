from pydantic import BaseModel

class CalorieRequest(BaseModel):
    dish_name: str
    servings: int

class CalorieResponse(BaseModel):
    dish_name: str
    servings: int
    calories_per_serving: float
    total_calories: float
    source: str
