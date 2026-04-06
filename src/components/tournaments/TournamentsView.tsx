'use client'

import { useState, useMemo } from 'react'
import type { Tournament } from '@/lib/types'
import { countryFlag } from '@/lib/formatters'

const CATEGORY_OPTIONS = ['ALL', 'PPA', 'MLP', 'SEA', 'Vietnam'] as const

export default function TournamentsView({ tournaments }: { tournaments: Tournament[] }) {
  const [activeCategory, setActiveCategory] = useState<string>('ALL')
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming')

  const filtered = useMemo(() => {
    let result = [...tournaments]
    if (activeCategory !== 'ALL') {
      result = result.filter((t) => t.category === activeCategory)
    }
    if (activeTab === 'upcoming') {
      result = result.filter((t) => t.status === 'upcoming' || t.status === 'live')
    } else {
      result = result.filter((t) => t.status === 'past')
    }
    return result
  }, [tournaments, activeCategory, activeTab])

  return (
    <div>
      {/* Category pills */}
      <div className="flex flex-wrap gap-2 mb-4">
        {CATEGORY_OPTIONS.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`font-condensed text-sm font-semibold uppercase tracking-wide px-3 py-1.5 rounded-pill transition-all duration-fast ${
              activeCategory === cat
                ? 'bg-ink text-white'
                : 'bg-bg2 text-ink3 hover:bg-bg3'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Upcoming / Past tabs */}
      <div className="flex border-b border-border mb-6">
        {(['upcoming', 'past'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`font-condensed text-sm font-bold uppercase tracking-wide px-4 py-2 border-b-2 transition-all ${
              activeTab === tab
                ? 'border-blue text-blue'
                : 'border-transparent text-ink4 hover:text-ink3'
            }`}
          >
            {tab === 'upcoming' ? 'Upcoming & Live' : 'Past'}
          </button>
        ))}
      </div>

      {/* Tournament cards */}
      <div className="space-y-3">
        {filtered.map((t) => (
          <div
            key={t.id}
            className="flex items-center gap-4 p-4 border border-border rounded-lg hover:bg-bg2 transition-colors"
          >
            {/* Status badge */}
            <div className="shrink-0">
              {t.status === 'live' && (
                <span className="inline-flex items-center gap-1.5 bg-red/10 text-red text-xs font-bold px-2 py-1 rounded-pill">
                  <span className="w-2 h-2 bg-red rounded-full animate-pulsate" />
                  LIVE
                </span>
              )}
              {t.status === 'upcoming' && (
                <span className="inline-flex items-center bg-blue/10 text-blue text-xs font-bold px-2 py-1 rounded-pill">
                  UPCOMING
                </span>
              )}
              {t.status === 'past' && (
                <span className="inline-flex items-center bg-bg3 text-ink4 text-xs font-bold px-2 py-1 rounded-pill">
                  COMPLETED
                </span>
              )}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                  {t.category}
                </span>
              </div>
              <h3 className="font-condensed text-lg font-bold uppercase leading-tight mt-0.5">
                {t.name}
              </h3>
              <p className="text-xs text-ink4 mt-1">
                {countryFlag(t.country)} {t.location} &middot;{' '}
                {new Date(t.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                {' - '}
                {new Date(t.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </p>
            </div>

            {/* Prize money */}
            {t.prize_money && (
              <div className="shrink-0 text-right">
                <span className="font-condensed text-xs font-bold uppercase text-ink4">Prize</span>
                <p className="font-condensed text-lg font-bold">
                  ${t.prize_money.toLocaleString()}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-ink4 text-sm py-8 text-center">No tournaments found.</p>
      )}
    </div>
  )
}
