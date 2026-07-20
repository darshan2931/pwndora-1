from datetime import timedelta
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.session import get_db
from models.sqlalchemy_models import User
from app.core import security
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(request: dict, db: Session = Depends(get_db)) -> Any:
    email = request.get("email")
    password = request.get("password")
    name = request.get("name", "User")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit")

    user = db.scalars(select(User).filter_by(email=email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # We use string conversion for PortableUUID compatibility
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        name=name,
        hashed_password=security.get_password_hash(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "data": {"id": str(user.id), "email": user.email, "name": user.name}}


@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = db.scalars(select(User).filter_by(email=form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            str(user.id), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/me")
def read_user_me(current_user: User = Depends(get_current_user)) -> Any:
    return {"success": True, "data": {"id": str(current_user.id), "email": current_user.email, "name": current_user.name}}
