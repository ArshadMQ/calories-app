import os
import jwt
from fastapi import Header, status
from jwt import PyJWTError
from app.models.model import User
from app.db.session import SessionLocal
from dotenv import load_dotenv
import pytz
import datetime as _datetime
from datetime import datetime, timedelta
from pytz import timezone

load_dotenv()
asia_kolkata = timezone("Asia/Kolkata")
utc = timezone("UTC")
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


def tz_now(tz: pytz = utc):
    dt = datetime.utcnow()
    return dt.replace(tzinfo=tz)


def get_timezone_from_offset(dt: datetime) -> str:
    if isinstance(dt.tzinfo, _datetime.timezone):
        offset = dt.utcoffset()
        now = tz_now()
        for tz in pytz.all_timezones:
            _timezone = pytz.timezone(tz)
            if now.astimezone(_timezone).utcoffset() == offset:
                return _timezone.zone
    else:
        return datetime.utcnow()


def days_ago(
        dt: datetime, days: int = 1, hours: int = 0, minutes: int = 0, seconds: int = 0
):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> days_ago(dt)
    datetime.datetime(2020, 7, 12, 21, 3, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    past = dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if dt.tzinfo:
        past = past.replace(tzinfo=dt.tzinfo)
    return past
