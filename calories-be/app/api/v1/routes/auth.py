from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserLogin
from app.models.model import User
from app.schemas.calories import LoginResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.session import db_session_connection

router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db_session: Session = Depends(db_session_connection)):
    if db_session.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return {"msg": "User created successfully",
            "status_code": status.HTTP_201_CREATED}


@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin, db_session: Session = Depends(db_session_connection)):
    user = db_session.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "Bearer", "status_code": status.HTTP_200_OK}
