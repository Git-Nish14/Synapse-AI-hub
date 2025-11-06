# app/routes/payments.py
import os
from datetime import datetime, timedelta

import stripe
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.db.database import SessionLocal
from app.db import models

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
SUCCESS_PATH = os.getenv("STRIPE_SUCCESS_PATH", "/payments/success")
CANCEL_PATH = os.getenv("STRIPE_CANCEL_PATH", "/payments/cancel")

router = APIRouter(prefix="/payments", tags=["Payments"])


def mark_user_premium(user_id: int):
    """Helper to safely mark a user as premium."""
    db = SessionLocal()
    try:
        user = db.query(models.User).get(user_id)
        if not user:
            return None
        user.is_premium = True
        user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
        db.commit()
        return user.username
    finally:
        db.close()


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    """Create a Stripe Checkout Session."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if user.is_premium:
        return JSONResponse({"detail": "Already premium"}, status_code=400)

    customer_id = getattr(user, "stripe_customer_id", None)
    if not customer_id:
        # Create Stripe customer
        customer = stripe.Customer.create(email=user.email, name=user.username)
        customer_id = customer["id"]

        # Persist customer_id
        db = SessionLocal()
        try:
            db_user = db.query(models.User).get(user.id)
            if db_user:
                db_user.stripe_customer_id = customer_id
                db.commit()
        finally:
            db.close()

    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Synapse Premium (Monthly)"},
                        "unit_amount": 999,  # $9.99
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=FRONTEND_URL + SUCCESS_PATH + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=FRONTEND_URL + CANCEL_PATH,
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Stripe webhook handler."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not WEBHOOK_SECRET:
        # Local debug: skip signature check
        event = stripe.Event.construct_from(stripe.util.json.loads(payload), stripe.api_key)
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        except Exception as e:
            return JSONResponse(
                {"error": f"Webhook signature verification failed: {str(e)}"},
                status_code=400
            )

    db = SessionLocal()
    try:
        # checkout.session.completed
        if event["type"] == "checkout.session.completed":
            session_data = event["data"]["object"]
            customer_id = session_data.get("customer")
            subscription_id = session_data.get("subscription")

            user = db.query(models.User).filter(models.User.stripe_customer_id == customer_id).first()
            if user:
                user.is_premium = True
                if subscription_id:
                    user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
                db.commit()

        # invoice.payment_succeeded (subscription renewal)
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            customer_id = invoice.get("customer")
            user = db.query(models.User).filter(models.User.stripe_customer_id == customer_id).first()
            if user:
                user.is_premium = True
                user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
                db.commit()
    finally:
        db.close()

    return JSONResponse({"status": "success"})


@router.post("/simulate-success/{user_id}")
async def simulate_payment_success(user_id: int):
    """
    Dev/testing only: simulate a Stripe payment success without Stripe CLI.
    """
    username = mark_user_premium(user_id)
    if not username:
        return JSONResponse({"detail": "User not found"}, status_code=404)

    return JSONResponse({"detail": f"User {username} is now premium"})
