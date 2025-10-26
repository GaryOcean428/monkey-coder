import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { productId, priceId, successUrl, cancelUrl } = body;

    const secret = process.env.STRIPE_SECRET_KEY;
    if (!secret) {
      return NextResponse.json({ error: 'Stripe not configured' }, { status: 500 });
    }
    const stripe = new Stripe(secret, {
      apiVersion: '2025-08-27.basil',
    });

    // TODO: Get the current user from the session
    // For now, we'll create a new customer or use an existing one

    // Create a checkout session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId || undefined,
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: successUrl,
      cancel_url: cancelUrl,
      allow_promotion_codes: true,
      billing_address_collection: 'required',
      customer_email: undefined, // TODO: Get from authenticated user
      metadata: {
        productId,
      },
    });

    return NextResponse.json({
      sessionId: session.id,
      sessionUrl: session.url
    });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    if (error instanceof Error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    return NextResponse.json({ error: 'Failed to create checkout session' }, { status: 500 });
  }
}
