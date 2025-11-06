from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class CreditPlan(Base):
    __tablename__ = "credit_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "Free", "Premium", "Pro"
    chat_credits = Column(Integer, default=10)
    image_credits = Column(Integer, default=5)
    refresh_interval = Column(Integer, default=60)  # in minutes
    price = Column(Float, default=0.0)  # price per month or one-time

    users = relationship("User", back_populates="plan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plan_id = Column(Integer, ForeignKey("credit_plans.id"), default=1)  # default = Free
    plan = relationship("CreditPlan", back_populates="users")

    credits = relationship(
        "Credit",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Credit(Base):
    __tablename__ = "credits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_credits = Column(Integer, default=10)
    image_credits = Column(Integer, default=5)
    last_reset = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="credits")
