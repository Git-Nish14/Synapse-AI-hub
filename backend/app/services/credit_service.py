# app/services/credit_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db import models


def reset_credits_if_needed(credit: models.Credit):
    """Handles automatic credit refresh based on time rules."""

    now = datetime.now(timezone.utc)
    last_reset = credit.last_reset

    # Ensure timezone-aware datetime
    if last_reset.tzinfo is None:
        last_reset = last_reset.replace(tzinfo=timezone.utc)

    # Hourly chat reset
    if now - last_reset >= timedelta(hours=1):
        credit.chat_credits = 10

    # Daily image reset
    if now.date() != last_reset.date():
        credit.image_credits = 5

    # Yearly reset
    if now.year != last_reset.year:
        credit.chat_credits = 10
        credit.image_credits = 5

    credit.last_reset = now


def deduct_credit(db: Session, user: models.User, credit_type: str):
    """Deducts credits and returns updated values"""

    if user.is_premium:
        return {
            "chat_credits": "unlimited",
            "image_credits": "unlimited",
            "last_reset": None
        }

    # Ensure user has a credit row
    if not user.credits:
        credit = models.Credit(user_id=user.id)
        db.add(credit)
        db.commit()
        db.refresh(credit)
    else:
        credit = user.credits[0]

    # Reset if needed before deduction
    reset_credits_if_needed(credit)

    # Deduct credit
    if credit_type == "chat":
        if credit.chat_credits <= 0:
            raise Exception("No chat credits left.")
        credit.chat_credits -= 1

    elif credit_type == "image":
        if credit.image_credits <= 0:
            raise Exception("No image credits left.")
        credit.image_credits -= 1

    else:
        raise Exception("Invalid credit type. Use 'chat' or 'image'.")

    db.add(credit)
    db.commit()
    db.refresh(credit)

    return {
        "chat_credits": credit.chat_credits,
        "image_credits": credit.image_credits,
        "last_reset": credit.last_reset
    }
