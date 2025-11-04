from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models

def reset_credits_if_needed(credit: models.Credit):
    now = datetime.utcnow()
    # Reset chat every hour
    if now - credit.last_reset >= timedelta(hours=1):
        credit.chat_credits = 10

    # Reset image credits daily
    if now.date() != credit.last_reset.date():
        credit.image_credits = 5

    # Reset for new year
    if now.year != credit.last_reset.year:
        credit.image_credits = 5
        credit.chat_credits = 10

    credit.last_reset = now


def deduct_credit(db: Session, user: models.User, type: str):
    if user.is_premium:
        return  # Premium users have unlimited credits

    credit = user.credits[0]
    reset_credits_if_needed(credit)

    if type == "chat":
        if credit.chat_credits <= 0:
            raise Exception("No chat credits left.")
        credit.chat_credits -= 1
    elif type == "image":
        if credit.image_credits <= 0:
            raise Exception("No image credits left.")
        credit.image_credits -= 1

    db.commit()
