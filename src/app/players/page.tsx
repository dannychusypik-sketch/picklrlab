import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import PlayersGrid from '@/components/players/PlayersGrid'
import { getPlayers } from '@/lib/supabase'

export const metadata: Metadata = {
  title: 'Players',
}

export default async function PlayersPage() {
  const players = await getPlayers()

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          Players
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Browse professional pickleball players from around the world.
        </p>
        <PlayersGrid players={players} />
      </main>
      <Footer />
    </>
  )
}
