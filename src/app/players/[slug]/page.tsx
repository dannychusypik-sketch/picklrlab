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

const DIVISIONS = [
  { key: 'mens_singles', label: "Men's Singles" },
  { key: 'womens_singles', label: "Women's Singles" },
  { key: 'mens_doubles', label: "Men's Doubles" },
  { key: 'womens_doubles', label: "Women's Doubles" },
  { key: 'mixed_doubles', label: 'Mixed Doubles' },
]

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

  // Fetch rankings across all divisions
  const allDivisionRankings = await Promise.all(
    DIVISIONS.map(async (div) => {
      const rankings = await getRankings(div.key)
      const playerRank = rankings.find((r) => r.player_id === player.id)
      return playerRank ? { division: div, ranking: playerRank } : null
    })
  )
  const playerDivisions = allDivisionRankings.filter(Boolean) as {
    division: { key: string; label: string }
    ranking: { rank: number; points: number; win_rate?: number; titles: number; delta: number }
  }[]

  // Use the best (lowest rank) as the primary ranking
  const primaryRanking = playerDivisions.length > 0
    ? playerDivisions.reduce((best, curr) => curr.ranking.rank < best.ranking.rank ? curr : best)
    : null

  return (
    <>
      <PersonSchema player={player} />
      <BreadcrumbSchema items={[
        { name: 'Home', url: 'https://picklrlab.com' },
        { name: 'Players', url: 'https://picklrlab.com/players' },
        { name: player.name, url: `https://picklrlab.com/players/${player.slug}` },
      ]} />
      <Nav />
      <main>
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-navy via-navy to-blue">
          <div className="max-w-site mx-auto px-5 py-10 md:py-14">
            {/* Breadcrumb */}
            <nav className="flex items-center gap-2 text-xs text-white/50 mb-8">
              <Link href="/" className="hover:text-white/80">Home</Link>
              <span>/</span>
              <Link href="/players" className="hover:text-white/80">Players</Link>
              <span>/</span>
              <span className="text-white/70">{player.name}</span>
            </nav>

            <div className="flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-10">
              {/* Player Photo */}
              {player.photo_url ? (
                <img
                  src={player.photo_url}
                  alt={player.name}
                  className="w-28 h-28 md:w-36 md:h-36 rounded-full object-cover border-4 border-white/20 shadow-xl"
                />
              ) : (
                <div className="w-28 h-28 md:w-36 md:h-36 rounded-full bg-white/10 border-4 border-white/20 flex items-center justify-center shadow-xl">
                  <span className="font-condensed text-5xl md:text-6xl font-bold text-white/40">
                    {player.name.charAt(0)}
                  </span>
                </div>
              )}

              {/* Name + Meta */}
              <div className="text-center md:text-left flex-1">
                <h1 className="font-condensed text-4xl md:text-5xl font-bold uppercase text-white leading-tight">
                  {player.name}
                </h1>
                <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mt-3">
                  {player.country && (
                    <span className="inline-flex items-center gap-1.5 bg-white/10 text-white/90 text-sm px-3 py-1 rounded-full">
                      {countryFlag(player.country)} {player.country}
                    </span>
                  )}
                  {player.sponsor && (
                    <span className="inline-flex items-center gap-1.5 bg-white/10 text-white/90 text-sm px-3 py-1 rounded-full">
                      {player.sponsor}
                    </span>
                  )}
                  {player.paddle && (
                    <span className="inline-flex items-center gap-1.5 bg-white/10 text-white/90 text-sm px-3 py-1 rounded-full">
                      {player.paddle}
                    </span>
                  )}
                  {player.birth_year && (
                    <span className="inline-flex items-center gap-1.5 bg-white/10 text-white/90 text-sm px-3 py-1 rounded-full">
                      Born {player.birth_year}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats Row */}
        {primaryRanking && (
          <div className="bg-bg2 border-b border-bd2">
            <div className="max-w-site mx-auto px-5 py-5">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="font-condensed text-xs font-bold uppercase tracking-wider text-ink4 mb-1">
                    Best Ranking
                  </div>
                  <div className="font-condensed text-3xl font-bold text-navy">
                    #{primaryRanking.ranking.rank}
                  </div>
                  <div className="text-xs text-ink4 mt-0.5">{primaryRanking.division.label}</div>
                </div>
                <div className="text-center">
                  <div className="font-condensed text-xs font-bold uppercase tracking-wider text-ink4 mb-1">
                    Points
                  </div>
                  <div className="font-condensed text-3xl font-bold text-navy">
                    {primaryRanking.ranking.points.toLocaleString()}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-condensed text-xs font-bold uppercase tracking-wider text-ink4 mb-1">
                    Win Rate
                  </div>
                  <div className="font-condensed text-3xl font-bold text-navy">
                    {primaryRanking.ranking.win_rate != null ? `${primaryRanking.ranking.win_rate}%` : '-'}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-condensed text-xs font-bold uppercase tracking-wider text-ink4 mb-1">
                    Titles
                  </div>
                  <div className="font-condensed text-3xl font-bold text-navy">
                    {primaryRanking.ranking.titles}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="max-w-site mx-auto px-5 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column: Division Rankings */}
            <div className="lg:col-span-1 space-y-6">
              {/* Division Rankings Card */}
              {playerDivisions.length > 0 && (
                <div className="bg-bg2 rounded-xl p-5 border border-bd2">
                  <h2 className="font-condensed text-lg font-bold uppercase tracking-wide mb-4">
                    Division Rankings
                  </h2>
                  <div className="space-y-3">
                    {playerDivisions.map(({ division, ranking }) => (
                      <div key={division.key} className="flex items-center justify-between py-2 border-b border-bd2 last:border-0">
                        <div>
                          <div className="text-sm font-semibold">{division.label}</div>
                          <div className="text-xs text-ink4">
                            {ranking.points.toLocaleString()} pts
                            {ranking.win_rate != null && ` · ${ranking.win_rate}% win`}
                          </div>
                        </div>
                        <div className="bg-gradient-to-br from-navy to-blue text-white rounded-lg px-3 py-1.5 text-center min-w-[52px]">
                          <span className="font-condensed text-lg font-bold">#{ranking.rank}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Player Info Card */}
              <div className="bg-bg2 rounded-xl p-5 border border-bd2">
                <h2 className="font-condensed text-lg font-bold uppercase tracking-wide mb-4">
                  Player Info
                </h2>
                <div className="space-y-3">
                  {player.country && (
                    <div className="flex justify-between text-sm">
                      <span className="text-ink4">Country</span>
                      <span className="font-semibold">{countryFlag(player.country)} {player.country}</span>
                    </div>
                  )}
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
            </div>

            {/* Right Column: Bio */}
            <div className="lg:col-span-2">
              {player.bio && (
                <div>
                  <h2 className="font-condensed text-xl font-bold uppercase tracking-wide mb-4">
                    Biography
                  </h2>
                  {player.bio.includes('<') ? (
                    <div
                      className="prose prose-sm max-w-none text-ink2 leading-relaxed [&_p]:mb-4 [&_a]:text-blue [&_a]:underline [&_h2]:font-condensed [&_h2]:text-lg [&_h2]:font-bold [&_h2]:uppercase [&_h2]:mt-6 [&_h2]:mb-2 [&_h3]:font-condensed [&_h3]:font-bold [&_h3]:mt-4 [&_h3]:mb-2"
                      dangerouslySetInnerHTML={{ __html: player.bio }}
                    />
                  ) : (
                    <p className="text-base text-ink2 leading-relaxed">{player.bio}</p>
                  )}
                </div>
              )}

              {!player.bio && (
                <div className="text-center py-12 text-ink4">
                  <p className="text-lg">No biography available yet.</p>
                  <p className="text-sm mt-2">Check back later for more information about {player.name}.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
