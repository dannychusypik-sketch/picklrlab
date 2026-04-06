'use client'

import { useState } from 'react'
import Link from 'next/link'
import type { Ranking } from '@/lib/types'
import { countryFlag } from '@/lib/formatters'

const categories = [
  { key: 'mens_singles', label: "Men's Singles" },
  { key: 'womens_singles', label: "Women's Singles" },
  { key: 'mixed_doubles', label: 'Mixed Doubles' },
]

export default function HomeRankings({ rankings }: { rankings: Ranking[] }) {
  const [activeCategory, setActiveCategory] = useState(categories[0].key)

  const filtered = rankings.filter((r) => r.category === activeCategory).slice(0, 10)

  return (
    <div className="max-w-site mx-auto px-5 py-6">
      {/* Category tabs */}
      <div className="flex gap-1 mb-4">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setActiveCategory(cat.key)}
            className={`font-condensed text-xs font-semibold uppercase tracking-wide px-3 py-1.5 rounded-pill transition-colors ${
              activeCategory === cat.key
                ? 'bg-green2 text-white'
                : 'bg-bg3 text-ink3 hover:bg-bg4'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Rankings table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-bd2 text-left">
              <th className="font-condensed text-xs font-semibold uppercase tracking-wide text-ink4 py-2 w-10">#</th>
              <th className="font-condensed text-xs font-semibold uppercase tracking-wide text-ink4 py-2">Player</th>
              <th className="font-condensed text-xs font-semibold uppercase tracking-wide text-ink4 py-2 text-right">Points</th>
              <th className="font-condensed text-xs font-semibold uppercase tracking-wide text-ink4 py-2 text-right hidden md:table-cell">Win %</th>
              <th className="font-condensed text-xs font-semibold uppercase tracking-wide text-ink4 py-2 text-right hidden md:table-cell">Titles</th>
              <th className="font-condensed text-xs font-semibold uppercase tracking-wide text-ink4 py-2 text-right w-14">+/-</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-bd2 hover:bg-bg2 transition-colors">
                <td className="py-2.5 font-mono font-bold text-ink4">{r.rank}</td>
                <td className="py-2.5">
                  <Link href={`/players/${r.player?.slug || ''}`} className="flex items-center gap-2 hover:text-blue">
                    <span>{r.player ? countryFlag(r.player.country) : ''}</span>
                    <span className="font-body font-semibold">{r.player?.name || 'Unknown'}</span>
                  </Link>
                </td>
                <td className="py-2.5 text-right font-mono">{r.points.toLocaleString()}</td>
                <td className="py-2.5 text-right font-mono hidden md:table-cell">{r.win_rate}%</td>
                <td className="py-2.5 text-right font-mono hidden md:table-cell">{r.titles}</td>
                <td className="py-2.5 text-right font-mono">
                  {r.delta > 0 && <span className="text-green2">+{r.delta}</span>}
                  {r.delta < 0 && <span className="text-red">{r.delta}</span>}
                  {r.delta === 0 && <span className="text-ink4">-</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* View all link */}
      <div className="mt-4 text-center">
        <Link
          href="/rankings"
          className="font-condensed text-sm font-semibold uppercase tracking-wide text-green2 hover:text-ink transition-colors"
        >
          View Full Rankings &rarr;
        </Link>
      </div>
    </div>
  )
}
