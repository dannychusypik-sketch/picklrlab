'use client'

import { useState } from 'react'
import Link from 'next/link'
import type { Article } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'

const tabs = ['All', 'PPA Tour', 'MLP', 'Gear', 'International', 'Tips']

function ArticleThumbnail({ article }: { article: Article }) {
  return article.image_url ? (
    <img
      src={article.image_url}
      alt={article.title}
      className="w-[80px] h-[56px] rounded object-cover shrink-0"
    />
  ) : (
    <div className="w-[80px] h-[56px] rounded shrink-0 bg-gradient-to-br from-navy to-blue flex items-center justify-center text-white/10 text-2xl font-condensed font-bold">
      {article.category.charAt(0).toUpperCase()}
    </div>
  )
}

export default function HomeNews({
  articles,
  mostRead,
}: {
  articles: Article[]
  mostRead: Pick<Article, 'id' | 'title' | 'slug' | 'category' | 'views'>[]
}) {
  const [activeTab, setActiveTab] = useState('All')

  const nonTraining = articles.filter((a) => a.category !== 'training')
  const filtered =
    activeTab === 'All'
      ? nonTraining
      : nonTraining.filter((a) => a.category === activeTab)

  return (
    <div className="max-w-site mx-auto px-5 py-6">
      {/* Tabs */}
      <div className="flex gap-1 mb-5 overflow-x-auto scrollbar-hide">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`font-condensed text-xs font-semibold uppercase tracking-wide px-3 py-1.5 rounded-pill whitespace-nowrap transition-colors ${
              activeTab === tab
                ? 'bg-ink text-white'
                : 'bg-bg3 text-ink3 hover:bg-bg4'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="grid md:grid-cols-[1fr_300px] gap-8">
        {/* Articles list */}
        <div>
          {filtered.slice(0, 10).map((article) => (
            <Link
              key={article.id}
              href={`/news/${article.slug}`}
              className="group flex gap-4 py-3.5 border-b border-bd2 hover:bg-bg2 transition-colors"
            >
              <ArticleThumbnail article={article} />
              <div className="flex-1 min-w-0">
                <p className="text-2xs text-ink4 uppercase tracking-wide font-semibold mb-1">
                  {article.category}
                </p>
                <h3 className="font-body text-md font-bold leading-snug group-hover:text-blue">
                  {article.title}
                </h3>
                {article.excerpt && (
                  <p className="text-xs text-ink4 mt-1 line-clamp-2">{article.excerpt}</p>
                )}
                <p className="text-2xs text-ink4/60 mt-1.5">
                  {article.author}
                  {article.published_at &&
                    ` · ${formatDistanceToNow(new Date(article.published_at), { addSuffix: true })}`}
                </p>
              </div>
            </Link>
          ))}
        </div>

        {/* Most Read sidebar */}
        <aside>
          <h3 className="font-condensed text-lg font-bold uppercase tracking-tight border-b-2 border-red pb-2 mb-3">
            Most Read
          </h3>
          <ol className="space-y-0">
            {mostRead.map((article, i) => (
              <li key={article.id} className="border-b border-bd2">
                <Link
                  href={`/news/${article.slug}`}
                  className="group flex items-start gap-3 py-3 hover:bg-bg2 transition-colors"
                >
                  <span className="font-condensed text-2xl font-bold text-ink4/30 leading-none mt-0.5">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-body text-sm font-bold leading-snug group-hover:text-blue">
                      {article.title}
                    </p>
                    <p className="text-2xs text-ink4 mt-1">
                      {article.views.toLocaleString()} views
                    </p>
                  </div>
                </Link>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </div>
  )
}
