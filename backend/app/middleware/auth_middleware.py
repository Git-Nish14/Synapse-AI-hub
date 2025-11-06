# app/middleware/auth_middleware.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.db.database import SessionLocal
from app.db import models
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # ✅ Skip auth checks for login/signup routes
        if path.startswith("/auth"):
            return await call_next(request)

        # ✅ Protect /api and /users routes
        protected_routes = ("/api", "/users", "/credits", "/payments")

        if path.startswith(protected_routes):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    {"detail": "Missing authorization token"}, status_code=401
                )

            token = auth_header.split(" ")[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email: str = payload.get("sub")
                if email is None:
                    raise HTTPException(status_code=401, detail="Invalid token payload")
            except JWTError:
                return JSONResponse(
                    {"detail": "Invalid or expired token"}, status_code=401
                )

            # Get user from DB
            db = SessionLocal()
            user = db.query(models.User).filter(models.User.email == email).first()
            db.close()

            if not user:
                return JSONResponse({"detail": "User not found"}, status_code=404)

            # Attach user to request
            request.state.user = user

        response = await call_next(request)
        return response
