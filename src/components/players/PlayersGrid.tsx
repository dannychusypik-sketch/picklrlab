'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import type { Player } from '@/lib/types'
import { countryFlag } from '@/lib/formatters'

export default function PlayersGrid({ players }: { players: Player[] }) {
  const [search, setSearch] = useState('')
  const [countryFilter, setCountryFilter] = useState('')

  const countries = useMemo(() => {
    const set = new Set(players.map((p) => p.country).filter(Boolean))
    return Array.from(set).sort()
  }, [players])

  const filtered = useMemo(() => {
    let result = [...players]
    if (search) {
      const q = search.toLowerCase()
      result = result.filter((p) => p.name.toLowerCase().includes(q))
    }
    if (countryFilter) {
      result = result.filter((p) => p.country === countryFilter)
    }
    return result
  }, [players, search, countryFilter])

  return (
    <div>
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <input
          type="text"
          placeholder="Search players..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm w-60 focus:outline-none focus:ring-2 focus:ring-blue/30"
        />
        <select
          value={countryFilter}
          onChange={(e) => setCountryFilter(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        >
          <option value="">All Countries</option>
          {countries.map((c) => (
            <option key={c} value={c}>{countryFlag(c)} {c}</option>
          ))}
        </select>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {filtered.map((player) => (
          <Link
            key={player.id}
            href={`/players/${player.slug}`}
            className="group border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-fast bg-white"
          >
            {/* Avatar placeholder */}
            <div className="aspect-square bg-gradient-to-br from-bg3 to-bg4 flex items-center justify-center">
              <span className="font-condensed text-4xl font-bold text-ink5">
                {player.name.charAt(0)}
              </span>
            </div>
            <div className="p-3">
              <h3 className="font-condensed text-sm font-bold uppercase leading-tight group-hover:text-blue transition-colors">
                {player.name}
              </h3>
              <p className="text-xs text-ink4 mt-1">
                {countryFlag(player.country)} {player.country}
              </p>
              {player.sponsor && (
                <p className="text-2xs text-ink5 mt-0.5">{player.sponsor}</p>
              )}
            </div>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-ink4 text-sm py-8 text-center">No players found.</p>
      )}
    </div>
  )
}
