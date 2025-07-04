# Meal Calorie Count Generator (FastAPI)

## Features
- User Registration & Login (JWT Auth)
- Calorie lookup using USDA FoodData API
- Token-based secure endpoints
- Modular FastAPI structure

## Setup
```bash
pip install -r requirements.txt
cp .env .env.example
uvicorn app.main:app --reload
```

## Endpoints
- POST /auth/register
- POST /auth/login
- POST /get-calories (JWT protected)
