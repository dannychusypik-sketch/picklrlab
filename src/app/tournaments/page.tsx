import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import TournamentsView from '@/components/tournaments/TournamentsView'
import { getTournaments } from '@/lib/supabase'

export const metadata: Metadata = {
  title: 'Tournaments',
}

export default async function TournamentsPage() {
  const tournaments = await getTournaments()

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          Tournaments
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Professional pickleball tournaments worldwide.
        </p>
        <TournamentsView tournaments={tournaments} />
      </main>
      <Footer />
    </>
  )
}
