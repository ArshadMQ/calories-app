import os
import jwt
from fastapi import Header, status
from jwt import PyJWTError
from app.models.user import User

from app.db.session import SessionLocal
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
ERROR_EMAIL_PASSWORD_IS_INCORRECT = "Please login with this correct email and password instead."

db_session = SessionLocal()


class AuthService:
    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return {
                    "errors": ERROR_EMAIL_PASSWORD_IS_INCORRECT,
                    "status_code": status.HTTP_404_NOT_FOUND,
                }
            return email
        except PyJWTError:
            return {
                "errors": ERROR_EMAIL_PASSWORD_IS_INCORRECT,
                "status_code": status.HTTP_404_NOT_FOUND,
            }

    @staticmethod
    async def verify(token: str):
        """Given a JWT it finds the current loggedIn session and returns the user id"""
        try:
            email = AuthService.verify_token(token)
            user_instance = db_session.query(User).filter(User.email == email).one_or_none()
            return user_instance
        except Exception as _:
            return {
                "errors": "Invalid Token",
                "status_code": status.HTTP_401_UNAUTHORIZED
            }
        finally:
            db_session.close()


async def current_user(authorizations: str = Header(None)):
    if not authorizations:
        return {"errors": "Unauthorized", "status_code": status.HTTP_401_UNAUTHORIZED}
    token = authorizations.split()[-1]
    user = await AuthService.verify(token=token)
    if not user:
        return {"errors": "Unauthorized", "status_code": status.HTTP_401_UNAUTHORIZED}
    return user
