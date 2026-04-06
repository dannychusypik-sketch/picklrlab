'use client'

import { useState, useMemo } from 'react'
import type { Ranking } from '@/lib/types'
import { countryFlag } from '@/lib/formatters'

type SortKey = 'rank' | 'points' | 'win_rate' | 'titles'

export default function RankingsView({ rankings }: { rankings: Ranking[] }) {
  const [search, setSearch] = useState('')
  const [countryFilter, setCountryFilter] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('rank')
  const [sortAsc, setSortAsc] = useState(true)

  const countries = useMemo(() => {
    const set = new Set(rankings.map((r) => r.player?.country).filter(Boolean) as string[])
    return Array.from(set).sort()
  }, [rankings])

  const filtered = useMemo(() => {
    let result = [...rankings]
    if (search) {
      const q = search.toLowerCase()
      result = result.filter((r) => r.player?.name.toLowerCase().includes(q))
    }
    if (countryFilter) {
      result = result.filter((r) => r.player?.country === countryFilter)
    }
    result.sort((a, b) => {
      const av = a[sortKey] ?? 0
      const bv = b[sortKey] ?? 0
      return sortAsc ? (av as number) - (bv as number) : (bv as number) - (av as number)
    })
    return result
  }, [rankings, search, countryFilter, sortKey, sortAsc])

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortAsc(!sortAsc)
    } else {
      setSortKey(key)
      setSortAsc(key === 'rank')
    }
  }

  function exportCSV() {
    const header = 'Rank,Player,Country,Points,Win Rate,Titles,Delta'
    const rows = filtered.map((r) =>
      [r.rank, r.player?.name ?? '', r.player?.country ?? '', r.points, r.win_rate ?? '', r.titles, r.delta].join(','),
    )
    const csv = [header, ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'picklrlab-rankings.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const sortIcon = (key: SortKey) => {
    if (sortKey !== key) return ''
    return sortAsc ? ' \u25B2' : ' \u25BC'
  }

  return (
    <div>
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <input
          type="text"
          placeholder="Search player..."
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
        <button
          onClick={exportCSV}
          className="ml-auto font-condensed text-xs font-bold uppercase tracking-wide bg-bg2 text-ink3 px-4 py-2 rounded-lg hover:bg-bg3 transition"
        >
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-ink">
              {([
                ['rank', 'Rank'],
                ['points', 'Points'],
                ['win_rate', 'Win %'],
                ['titles', 'Titles'],
              ] as [SortKey, string][]).map(([key, label]) => (
                <th
                  key={key}
                  onClick={() => toggleSort(key)}
                  className="font-condensed text-xs font-bold uppercase tracking-wider text-left py-2 px-2 cursor-pointer select-none hover:text-blue transition"
                >
                  {label}{sortIcon(key)}
                </th>
              ))}
              <th className="font-condensed text-xs font-bold uppercase tracking-wider text-left py-2 px-2">
                Player
              </th>
              <th className="font-condensed text-xs font-bold uppercase tracking-wider text-left py-2 px-2">
                Country
              </th>
              <th className="font-condensed text-xs font-bold uppercase tracking-wider text-right py-2 px-2">
                +/-
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-border hover:bg-bg2 transition-colors">
                <td className="font-condensed text-lg font-bold py-2.5 px-2">{r.rank}</td>
                <td className="py-2.5 px-2 font-semibold">{r.points.toLocaleString()}</td>
                <td className="py-2.5 px-2">{r.win_rate != null ? `${r.win_rate}%` : '-'}</td>
                <td className="py-2.5 px-2">{r.titles}</td>
                <td className="py-2.5 px-2 font-semibold">{r.player?.name ?? 'Unknown'}</td>
                <td className="py-2.5 px-2">
                  {r.player?.country && (
                    <span>{countryFlag(r.player.country)} {r.player.country}</span>
                  )}
                </td>
                <td className="py-2.5 px-2 text-right">
                  {r.delta > 0 && <span className="text-green2 font-bold">+{r.delta}</span>}
                  {r.delta < 0 && <span className="text-red font-bold">{r.delta}</span>}
                  {r.delta === 0 && <span className="text-ink4">-</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <p className="text-ink4 text-sm py-8 text-center">No rankings match your filters.</p>
      )}
    </div>
  )
}
