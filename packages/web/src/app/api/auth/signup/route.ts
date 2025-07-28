import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-06-30.basil',
})

export async function POST(request: NextRequest) {
  try {
    const { name, email, password, plan } = await request.json()

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10)

    // TODO: Save user to database
    // For now, we'll simulate user creation
    const user = {
      id: Math.random().toString(36).substr(2, 9),
      name,
      email,
      plan,
      createdAt: new Date(),
    }

    // If Pro plan, create Stripe checkout session
    if (plan === 'pro') {
      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: [
          {
            price_data: {
              currency: 'usd',
              product_data: {
                name: 'Monkey Coder Pro',
                description: 'Unlimited code generation for professional developers',
                images: ['https://monkey-coder.com/logo.png'],
              },
              unit_amount: 2900, // $29.00
              recurring: {
                interval: 'month',
              },
            },
            quantity: 1,
          },
        ],
        mode: 'subscription',
        success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/signup`,
        customer_email: email,
        metadata: {
          userId: user.id,
          plan: 'pro',
        },
      })

      return NextResponse.json({
        success: true,
        checkoutUrl: session.url,
        userId: user.id,
      })
    }

    // For free plan, just return success
    return NextResponse.json({
      success: true,
      userId: user.id,
      message: 'Account created successfully',
    })

  } catch (error) {
    console.error('Signup error:', error)
    return NextResponse.json(
      { error: 'Failed to create account' },
      { status: 500 }
    )
  }
}
