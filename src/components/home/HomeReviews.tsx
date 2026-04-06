import Link from 'next/link'
import type { Paddle } from '@/lib/types'

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-2xs text-ink4 w-16 text-right">{label}</span>
      <div className="flex-1 h-1.5 bg-bg3 rounded-full overflow-hidden">
        <div
          className="h-full bg-red rounded-full"
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-2xs font-mono font-bold w-6 text-right">{score}</span>
    </div>
  )
}

function ReviewItem({ paddle }: { paddle: Paddle }) {
  return (
    <Link
      href={`/reviews/${paddle.slug}`}
      className="block border border-bd2 rounded-md p-4 hover:shadow-md transition-shadow bg-bg"
    >
      <div className="flex items-start gap-4">
        {/* Score badge */}
        <div className="flex-shrink-0 w-14 h-14 rounded-md bg-red flex items-center justify-center">
          <span className="font-condensed text-2xl font-bold text-white">
            {paddle.score_overall}
          </span>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <p className="text-2xs text-ink4 uppercase tracking-wide font-semibold">{paddle.brand}</p>
          <h3 className="font-condensed text-lg font-bold uppercase leading-tight mt-0.5">
            {paddle.name}
          </h3>
          {paddle.price_usd && (
            <p className="text-sm text-ink4 mt-1">${paddle.price_usd}</p>
          )}
        </div>
      </div>

      {/* Score bars */}
      <div className="mt-3 space-y-1.5">
        <ScoreBar label="Control" score={paddle.score_control ?? 0} />
        <ScoreBar label="Power" score={paddle.score_power ?? 0} />
        <ScoreBar label="Spin" score={paddle.score_spin ?? 0} />
        <ScoreBar label="Feel" score={paddle.score_feel ?? 0} />
      </div>

      {/* Verdict */}
      {paddle.verdict && (
        <p className="text-xs text-ink3 mt-3 italic leading-relaxed">&ldquo;{paddle.verdict}&rdquo;</p>
      )}
    </Link>
  )
}

export default function HomeReviews({ paddles }: { paddles: Paddle[] }) {
  const featured = paddles.filter((p) => p.featured).slice(0, 3)
  const items = featured.length ? featured : paddles.slice(0, 3)

  return (
    <div className="max-w-site mx-auto px-5 py-6">
      <div className="grid md:grid-cols-3 gap-4">
        {items.map((paddle) => (
          <ReviewItem key={paddle.id} paddle={paddle} />
        ))}
      </div>
      <div className="mt-4 text-center">
        <Link
          href="/reviews"
          className="font-condensed text-sm font-semibold uppercase tracking-wide text-red hover:text-ink transition-colors"
        >
          View All Reviews &rarr;
        </Link>
      </div>
    </div>
  )
}
