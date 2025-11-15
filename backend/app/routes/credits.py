# app/routes/credits.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.services.credit_service import reset_credits_if_needed, deduct_credit

router = APIRouter()


# --------------------------------------
# GET USER CREDIT STATUS
# --------------------------------------
@router.get("/{user_id}")
def get_user_credits(user_id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.credits:
        raise HTTPException(status_code=404, detail="Credits not initialized")

    credit = user.credits[0]

    # Apply reset logic before returning
    reset_credits_if_needed(credit)
    db.commit()
    db.refresh(credit)

    return {
        "user_id": user.id,
        "username": user.username,
        "chat_credits": credit.chat_credits,
        "image_credits": credit.image_credits,
        "last_reset": credit.last_reset,
        "is_premium": user.is_premium
    }


# --------------------------------------
# DEDUCT CREDITS
# --------------------------------------
@router.post("/deduct/{user_id}/{credit_type}")
def deduct_user_credit(user_id: int, credit_type: str, db: Session = Depends(get_db)):
    """
    Deduct one chat/image credit and return updated values.
    credit_type must be: 'chat' or 'image'
    """

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        updated_credits = deduct_credit(db, user, credit_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "user_id": user.id,
        "username": user.username,
        "updated_credits": updated_credits
    }
