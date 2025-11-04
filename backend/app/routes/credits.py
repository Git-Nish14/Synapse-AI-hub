from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.services.auth_service import verify_password, create_access_token
from app.services.credit_service import reset_credits_if_needed
from app.schemas import UserResponse
from datetime import datetime

router = APIRouter()

@router.get("/{user_id}")
def get_user_credits(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.credits:
        raise HTTPException(status_code=404, detail="Credits not initialized")

    credit = user.credits[0]
    reset_credits_if_needed(credit)
    db.commit()

    return {
        "user_id": user.id,
        "username": user.username,
        "is_premium": user.is_premium,
        "chat_credits": credit.chat_credits,
        "image_credits": credit.image_credits,
        "last_reset": credit.last_reset
    }
