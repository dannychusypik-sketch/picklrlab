import Link from 'next/link'
import type { Article } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'

export default function MoreStories({ articles }: { articles: Article[] }) {
  if (!articles.length) return null

  return (
    <div className="max-w-site mx-auto px-5">
      {articles.map((article) => (
        <Link
          key={article.id}
          href={`/news/${article.slug}`}
          className="group flex items-center justify-between gap-5 py-3.5 border-b border-bd2 hover:bg-bg2 transition-colors"
        >
          <span className="font-body text-md font-bold leading-snug flex-1 group-hover:text-blue">
            {article.title}
          </span>
          <span className="text-xs text-ink3/60 whitespace-nowrap">
            {article.published_at
              ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true })
              : ''}
          </span>
        </Link>
      ))}
    </div>
  )
}
