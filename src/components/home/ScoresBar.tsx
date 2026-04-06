import type { Match } from '@/lib/types'
import ScoreCard from '@/components/ui/ScoreCard'

export default function ScoresBar({ matches }: { matches: Match[] }) {
  if (!matches.length) return null

  return (
    <div className="bg-bg border-b border-bd2 py-3">
      <div className="max-w-site mx-auto px-5 flex gap-2.5 overflow-x-auto scrollbar-hide">
        {matches.map((match) => (
          <ScoreCard key={match.id} match={match} />
        ))}
      </div>
    </div>
  )
}
