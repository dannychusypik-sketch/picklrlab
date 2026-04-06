import type { Metadata } from 'next'
import Link from 'next/link'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import { getPlayers, getPlayerBySlug, getRankings } from '@/lib/supabase'
import { countryFlag } from '@/lib/formatters'
import { PersonSchema, BreadcrumbSchema } from '@/components/seo/JsonLd'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  const players = await getPlayers()
  return players.slice(0, 10).map((p) => ({ slug: p.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const player = await getPlayerBySlug(slug)
  if (!player) return { title: 'Player Not Found' }
  return {
    title: player.name,
    description: player.bio ?? `${player.name} — professional pickleball player.`,
  }
}

export default async function PlayerProfilePage({ params }: Props) {
  const { slug } = await params
  const player = await getPlayerBySlug(slug)

  if (!player) {
    return (
      <>
        <Nav />
        <main className="max-w-site mx-auto px-5 py-20 text-center">
          <h1 className="font-condensed text-3xl font-bold uppercase">Player Not Found</h1>
          <Link href="/players" className="text-blue mt-4 inline-block hover:underline">
            Back to Players
          </Link>
        </main>
        <Footer />
      </>
    )
  }

  // Find rankings for this player
  const mensRankings = await getRankings('mens_singles')
  const womensRankings = await getRankings('womens_singles')
  const allRankings = [...mensRankings, ...womensRankings]
  const playerRanking = allRankings.find((r) => r.player_id === player.id)

  return (
    <>
      <PersonSchema player={player} />
      <BreadcrumbSchema items={[
        { name: 'Home', url: 'https://picklrlab.com' },
        { name: 'Players', url: 'https://picklrlab.com/players' },
        { name: player.name, url: `https://picklrlab.com/players/${player.slug}` },
      ]} />
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs text-ink4 mb-6">
          <Link href="/" className="hover:text-blue">Home</Link>
          <span>/</span>
          <Link href="/players" className="hover:text-blue">Players</Link>
          <span>/</span>
          <span className="text-ink3">{player.name}</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Avatar + basic info */}
          <div>
            {/* Avatar placeholder */}
            <div className="w-full aspect-square max-w-[300px] bg-gradient-to-br from-bg3 to-bg4 rounded-lg flex items-center justify-center">
              <span className="font-condensed text-8xl font-bold text-ink5">
                {player.name.charAt(0)}
              </span>
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-ink4">Country</span>
                <span className="font-semibold">{countryFlag(player.country)} {player.country}</span>
              </div>
              {player.birth_year && (
                <div className="flex justify-between text-sm">
                  <span className="text-ink4">Birth Year</span>
                  <span className="font-semibold">{player.birth_year}</span>
                </div>
              )}
              {player.sponsor && (
                <div className="flex justify-between text-sm">
                  <span className="text-ink4">Sponsor</span>
                  <span className="font-semibold">{player.sponsor}</span>
                </div>
              )}
              {player.paddle && (
                <div className="flex justify-between text-sm">
                  <span className="text-ink4">Paddle</span>
                  <span className="font-semibold">{player.paddle}</span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Name, ranking, bio */}
          <div className="lg:col-span-2">
            <h1 className="font-condensed text-4xl font-bold uppercase leading-tight">
              {player.name}
            </h1>

            {playerRanking && (
              <div className="flex items-center gap-4 mt-4">
                <div className="bg-gradient-to-br from-navy to-blue text-white rounded-lg px-4 py-2">
                  <span className="font-condensed text-xs font-bold uppercase tracking-wider block">
                    World Rank
                  </span>
                  <span className="font-condensed text-3xl font-bold">
                    #{playerRanking.rank}
                  </span>
                </div>
                <div className="space-y-1 text-sm">
                  <p><span className="text-ink4">Points:</span> <span className="font-semibold">{playerRanking.points.toLocaleString()}</span></p>
                  <p><span className="text-ink4">Win Rate:</span> <span className="font-semibold">{playerRanking.win_rate}%</span></p>
                  <p><span className="text-ink4">Titles:</span> <span className="font-semibold">{playerRanking.titles}</span></p>
                </div>
              </div>
            )}

            {player.bio && (
              <div className="mt-6">
                <h2 className="font-condensed text-lg font-bold uppercase tracking-wide mb-2">
                  Biography
                </h2>
                <p className="text-base text-ink2 leading-relaxed">{player.bio}</p>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
