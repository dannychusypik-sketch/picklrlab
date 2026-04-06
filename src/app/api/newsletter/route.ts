import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email } = body

    if (!email || typeof email !== 'string' || !email.includes('@')) {
      return NextResponse.json(
        { error: 'A valid email address is required.' },
        { status: 400 },
      )
    }

    const normalizedEmail = email.toLowerCase().trim()

    // Attempt to insert into newsletter_subscribers table
    const { error } = await supabase
      .from('newsletter_subscribers')
      .insert({ email: normalizedEmail })

    if (error) {
      // Duplicate email (unique constraint)
      if (error.code === '23505') {
        return NextResponse.json(
          { message: 'You are already subscribed.' },
          { status: 200 },
        )
      }
      throw error
    }

    return NextResponse.json(
      { message: 'Successfully subscribed to the newsletter.' },
      { status: 201 },
    )
  } catch {
    return NextResponse.json(
      { error: 'Failed to subscribe. Please try again later.' },
      { status: 500 },
    )
  }
}
