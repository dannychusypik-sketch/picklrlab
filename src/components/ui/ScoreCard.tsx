import type { Match } from '@/lib/types'
import { countryFlag } from '@/lib/formatters'

const statusStyles = {
  live: 'bg-red text-white animate-pulsate',
  done: 'bg-ink4 text-white',
  upcoming: 'bg-blue text-white',
}

const statusLabel = {
  live: 'LIVE',
  done: 'FINAL',
  upcoming: 'UPCOMING',
}

export default function ScoreCard({ match }: { match: Match }) {
  return (
    <div className="flex-shrink-0 w-[220px] rounded-md border border-bd2 bg-bg p-3 text-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="font-condensed text-2xs font-semibold uppercase tracking-wide text-ink4 truncate max-w-[140px]">
          {match.tournament}
        </span>
        <span className={`text-2xs font-bold px-1.5 py-0.5 rounded ${statusStyles[match.status]}`}>
          {statusLabel[match.status]}
        </span>
      </div>

      {/* Round */}
      {match.round && (
        <p className="text-2xs text-ink4 mb-1.5">{match.round} &middot; {match.category}</p>
      )}

      {/* Players */}
      <div className="space-y-1">
        <div className={`flex items-center justify-between ${match.status === 'done' && (match.score_p1 ?? 0) > (match.score_p2 ?? 0) ? 'font-bold' : ''}`}>
          <span className="truncate flex-1">
            {match.player1 ? `${countryFlag(match.player1.country)} ${match.player1.name}` : 'TBD'}
          </span>
          <span className="ml-2 font-mono font-bold">{match.score_p1 ?? '-'}</span>
        </div>
        <div className={`flex items-center justify-between ${match.status === 'done' && (match.score_p2 ?? 0) > (match.score_p1 ?? 0) ? 'font-bold' : ''}`}>
          <span className="truncate flex-1">
            {match.player2 ? `${countryFlag(match.player2.country)} ${match.player2.name}` : 'TBD'}
          </span>
          <span className="ml-2 font-mono font-bold">{match.score_p2 ?? '-'}</span>
        </div>
      </div>
    </div>
  )
}
