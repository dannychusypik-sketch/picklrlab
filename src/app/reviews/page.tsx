import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import ReviewsGrid from '@/components/reviews/ReviewsGrid'
import { getPaddles } from '@/lib/supabase'

export const metadata: Metadata = {
  title: 'Paddle Reviews',
}

export default async function ReviewsPage() {
  const paddles = await getPaddles()

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          Paddle Reviews
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Lab-tested reviews with objective scores across 6 performance categories.
        </p>
        <ReviewsGrid paddles={paddles} />
      </main>
      <Footer />
    </>
  )
}
