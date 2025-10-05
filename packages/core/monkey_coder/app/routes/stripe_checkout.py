from typing import Optional

import os
import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

router = APIRouter()


class CheckoutRequest(BaseModel):
    productId: Optional[str] = None
    priceId: Optional[str] = None
    successUrl: HttpUrl
    cancelUrl: HttpUrl
    mode: Optional[str] = "subscription"  # "payment" | "subscription"


@router.post("/create-checkout-session")
async def create_checkout_session(payload: CheckoutRequest):
    secret = os.getenv("STRIPE_SECRET_KEY")
    if not secret:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    try:
        stripe.api_key = secret

        if not payload.priceId:
            raise HTTPException(status_code=400, detail="priceId is required")

        mode = payload.mode or "subscription"
        if mode not in ("subscription", "payment"):
            mode = "subscription"

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": payload.priceId,
                    "quantity": 1,
                }
            ],
            mode=mode,
            success_url=str(payload.successUrl),
            cancel_url=str(payload.cancelUrl),
            allow_promotion_codes=True,
            billing_address_collection="required",
            metadata={
                "productId": payload.productId or "",
            },
        )

        return {
            "sessionId": session.id,
            "sessionUrl": session.url,
        }
    except stripe.error.StripeError as e:
        # Surface Stripe error details where possible
        raise HTTPException(status_code=e.http_status or 400, detail=e.user_message or str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create checkout session") from e
