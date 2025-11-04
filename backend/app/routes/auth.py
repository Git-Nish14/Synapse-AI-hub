from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.services.credit_service import reset_credits_if_needed
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Give default credits
    new_credit = models.Credit(
        user_id=new_user.id,
        chat_credits=10,
        image_credits=5,
        last_reset=datetime.utcnow()
    )
    db.add(new_credit)
    db.commit()

    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Refresh credits
    if user.credits:
        reset_credits_if_needed(user.credits[0])
        db.commit()

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token}
