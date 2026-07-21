from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.session import get_db
from models.sqlalchemy_models import User
from app.core import security
from core.errors import raise_error, ErrorCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = security.decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise_error(401, ErrorCode.UNAUTHORIZED, "Could not validate credentials")
    except ValueError:
        raise_error(401, ErrorCode.UNAUTHORIZED, "Could not validate credentials")

    user = db.scalars(select(User).filter_by(id=user_id)).first()
    if user is None:
        raise_error(401, ErrorCode.UNAUTHORIZED, "Could not validate credentials")
    return user
