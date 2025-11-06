from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


# Helper to get current user from middleware
def get_current_user_from_request(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ✅ GET current logged-in user
@router.get("/me")
def get_current_user_profile(request: Request):
    user = get_current_user_from_request(request)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_premium": user.is_premium,
        "plan_id": user.plan_id,
        "created_at": user.created_at,
    }


# ✅ GET all users (optional admin restriction)
@router.get("/")
def get_all_users(db: Session = Depends(get_db), request: Request = None):
    current_user = get_current_user_from_request(request)
    # TODO: Add admin check if needed
    users = db.query(models.User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_premium": u.is_premium,
            "created_at": u.created_at,
            "plan_id": u.plan_id,
        }
        for u in users
    ]
