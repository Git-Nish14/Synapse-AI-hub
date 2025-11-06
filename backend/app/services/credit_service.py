from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db import models

def reset_credits_if_needed(credit: models.Credit):
    now = datetime.now(timezone.utc)
    last_reset = credit.last_reset

    if last_reset.tzinfo is None:
        last_reset = last_reset.replace(tzinfo=timezone.utc)

    # Reset chat every hour
    if now - last_reset >= timedelta(hours=1):
        credit.chat_credits = 10

    # Reset image daily
    if now.date() != last_reset.date():
        credit.image_credits = 5

    # Reset for new year
    if now.year != last_reset.year:
        credit.chat_credits = 10
        credit.image_credits = 5

    credit.last_reset = now

def deduct_credit(db: Session, user: models.User, type: str):
    if user.is_premium:
        return  # Premium users have unlimited credits

    credit = user.credits[0]  # Ensure user always has a credit row
    reset_credits_if_needed(credit)

    if type == "chat":
        if credit.chat_credits <= 0:
            raise Exception("No chat credits left.")
        credit.chat_credits -= 1
    elif type == "image":
        if credit.image_credits <= 0:
            raise Exception("No image credits left.")

    db.commit()
