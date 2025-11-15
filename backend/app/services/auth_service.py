# app/services/auth_service.py

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
import os

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"   # force modern bcrypt ident (fixes backend issues)
)


def hash_password(password: str) -> str:
    if password is None:
        raise HTTPException(status_code=400, detail="Password is required")

    # Ensure string
    password = str(password)

    # bcrypt max = 72 bytes → musttruncate **bytes**, not characters
    safe_pw = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

    try:
        return pwd_context.hash(safe_pw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password hashing failed: {e}")


def verify_password(password: str, hashed_password: str) -> bool:
    if password is None:
        return False

    password = str(password)

    # same truncation for check
    safe_pw = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

    return pwd_context.verify(safe_pw, hashed_password)


def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = data.copy()
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
