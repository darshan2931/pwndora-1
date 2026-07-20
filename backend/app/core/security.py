import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_secret_key = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET")
if not _secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is required. "
        "Set it to a strong, unique value (at least 32 characters)."
    )
SECRET_KEY = _secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
