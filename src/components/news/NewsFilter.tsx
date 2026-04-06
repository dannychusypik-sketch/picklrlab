'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import type { Article } from '@/lib/types'

const CATEGORIES = [
  'ALL', 'PPA TOUR', 'MLP', 'RANKINGS', 'REVIEWS', 'SEA', 'VIETNAM', 'GEAR', 'TRAINING', 'OPINION',
] as const

const PAGE_SIZE = 12

function timeAgo(dateStr?: string): string {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function NewsFilter({ articles }: { articles: Article[] }) {
  const [active, setActive] = useState<string>('ALL')
  const [visible, setVisible] = useState(PAGE_SIZE)

  const filtered = useMemo(() => {
    if (active === 'ALL') return articles
    return articles.filter(
      (a) => a.category.toUpperCase() === active || a.category.toUpperCase().includes(active),
    )
  }, [articles, active])

  const shown = filtered.slice(0, visible)
  const hasMore = visible < filtered.length

  return (
    <div>
      {/* Category tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => { setActive(cat); setVisible(PAGE_SIZE) }}
            className={`font-condensed text-sm font-semibold uppercase tracking-wide px-3 py-1.5 rounded-pill transition-all duration-fast ${
              active === cat
                ? 'bg-ink text-white'
                : 'bg-bg2 text-ink3 hover:bg-bg3'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Card grid */}
      <div className="flex flex-wrap gap-2">
        {shown.map((article) => (
          <Link
            key={article.id}
            href={`/news/${article.slug}`}
            className="w-[300px] bg-white border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-fast"
          >
            {/* Gradient placeholder image */}
            <div className="h-[170px] bg-gradient-to-br from-navy via-blue to-ink" />
            <div className="p-3">
              <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                {article.category}
              </span>
              <h3 className="font-condensed text-md font-bold uppercase leading-tight mt-1 line-clamp-3">
                {article.title}
              </h3>
              <p className="text-xs text-ink4 mt-2">{timeAgo(article.published_at)}</p>
            </div>
          </Link>
        ))}
      </div>

      {shown.length === 0 && (
        <p className="text-ink4 text-sm py-8 text-center">No articles found in this category.</p>
      )}

      {/* Load more */}
      {hasMore && (
        <div className="flex justify-center mt-8">
          <button
            onClick={() => setVisible((v) => v + PAGE_SIZE)}
            className="font-condensed text-sm font-bold uppercase tracking-wide bg-ink text-white px-6 py-2.5 rounded-pill hover:bg-ink2 transition-colors duration-fast"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  )
}
