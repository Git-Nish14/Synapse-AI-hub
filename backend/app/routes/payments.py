# app/routes/payments.py
import stripe
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.db.database import SessionLocal
from app.db import models
import os

router = APIRouter(prefix="/payments", tags=["Payments"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    user = request.state.user
    if user.is_premium:
        return JSONResponse({"detail": "User already premium"}, status_code=400)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Synapse Premium Plan"},
                    "unit_amount": 999,  # $9.99
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=os.getenv("FRONTEND_URL") + "/success",
            cancel_url=os.getenv("FRONTEND_URL") + "/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return JSONResponse({"error": "Invalid signature"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email")

        db = SessionLocal()
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            user.is_premium = True
            db.commit()
        db.close()

    return JSONResponse({"status": "success"})
