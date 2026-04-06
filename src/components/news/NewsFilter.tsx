'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import type { Article } from '@/lib/types'

const CATEGORIES = [
  'ALL', 'TOURNAMENTS', 'REVIEWS', 'RANKINGS', 'TRAINING', 'GEAR', 'SEA', 'VIETNAM', 'OPINION',
] as const

const PAGE_SIZE = 8

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

function ArticleImage({ article, className }: { article: Article; className: string }) {
  return article.image_url ? (
    <img src={article.image_url} alt={article.title} className={`${className} object-cover`} />
  ) : (
    <div className={`${className} bg-gradient-to-br from-navy to-blue flex items-center justify-center text-white/10 text-6xl font-condensed font-bold`}>
      {article.category.charAt(0).toUpperCase()}
    </div>
  )
}

export default function NewsFilter({ articles, featuredId }: { articles: Article[]; featuredId?: string }) {
  const [active, setActive] = useState<string>('ALL')
  const [visible, setVisible] = useState(PAGE_SIZE)

  const filtered = useMemo(() => {
    const base = featuredId ? articles.filter((a) => a.id !== featuredId) : articles
    if (active === 'ALL') return base
    return base.filter(
      (a) => a.category.toUpperCase() === active || a.category.toUpperCase().includes(active),
    )
  }, [articles, active, featuredId])

  const topTwo = filtered.slice(0, 2)
  const remaining = filtered.slice(2, visible)
  const hasMore = visible < filtered.length

  return (
    <div>
      {/* Category tabs - horizontal scrollable pills */}
      <nav className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide pb-1">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => { setActive(cat); setVisible(PAGE_SIZE) }}
            className={`font-condensed text-sm font-semibold uppercase tracking-wide px-4 py-2 rounded-pill whitespace-nowrap transition-all duration-fast ${
              active === cat
                ? 'bg-ink text-white'
                : 'bg-bg2 text-ink3 hover:bg-bg3'
            }`}
          >
            {cat}
          </button>
        ))}
      </nav>

      {/* Top 2 articles: side-by-side medium cards */}
      {topTwo.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {topTwo.map((article) => (
            <Link
              key={article.id}
              href={`/news/${article.slug}`}
              className="group bg-white border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-fast"
            >
              <div className="h-[200px] overflow-hidden">
                <ArticleImage
                  article={article}
                  className="w-full h-full group-hover:scale-[1.03] transition-transform duration-med"
                />
              </div>
              <div className="p-4">
                <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                  {article.category}
                </span>
                <h3 className="font-condensed text-lg font-bold uppercase leading-tight mt-1 line-clamp-2 group-hover:text-blue transition-colors">
                  {article.title}
                </h3>
                {article.excerpt && (
                  <p className="text-xs text-ink4 mt-2 line-clamp-2">{article.excerpt}</p>
                )}
                <p className="text-2xs text-ink4/60 mt-2">{timeAgo(article.published_at)}</p>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Remaining: list with thumbnails */}
      {remaining.length > 0 && (
        <div className="divide-y divide-border">
          {remaining.map((article) => (
            <Link
              key={article.id}
              href={`/news/${article.slug}`}
              className="group flex gap-4 py-4 hover:bg-bg2/50 transition-colors"
            >
              <div className="w-[120px] h-[80px] rounded overflow-hidden shrink-0">
                <ArticleImage article={article} className="w-full h-full" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                    {article.category}
                  </span>
                  <span className="text-2xs text-ink4/50">{timeAgo(article.published_at)}</span>
                </div>
                <h3 className="font-body text-md font-bold leading-snug group-hover:text-blue transition-colors line-clamp-2">
                  {article.title}
                </h3>
                {article.excerpt && (
                  <p className="text-xs text-ink4 mt-1 line-clamp-1 hidden sm:block">{article.excerpt}</p>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      {filtered.length === 0 && (
        <p className="text-ink4 text-sm py-8 text-center">No articles found in this category.</p>
      )}

      {/* Load more */}
      {hasMore && (
        <div className="flex justify-center mt-8">
          <button
            onClick={() => setVisible((v) => v + PAGE_SIZE)}
            className="font-condensed text-sm font-bold uppercase tracking-wide bg-ink text-white px-8 py-2.5 rounded-pill hover:bg-ink2 transition-colors duration-fast"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  )
}
