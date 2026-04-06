import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import RankingsView from '@/components/rankings/RankingsView'
import { getRankings } from '@/lib/supabase'

export const metadata: Metadata = {
  title: 'World Rankings',
}

export default async function RankingsPage() {
  const rankings = await getRankings('mens_singles')

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          World Rankings
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Official PicklrLab world pickleball rankings, updated quarterly.
        </p>
        <RankingsView rankings={rankings} />
      </main>
      <Footer />
    </>
  )
}
