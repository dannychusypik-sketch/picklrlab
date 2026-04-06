import Link from 'next/link'
import type { Article } from '@/lib/types'

const gradients = [
  'linear-gradient(135deg, #1a3060, #0059b5)',
  'linear-gradient(135deg, #0a5c36, #14a05c)',
  'linear-gradient(135deg, #d0021b, #ff4444)',
]

export default function FeaturedStories({ articles }: { articles: Article[] }) {
  const items = articles.slice(0, 3)
  if (!items.length) return null

  return (
    <div className="max-w-site mx-auto">
      <div className="md:grid md:grid-cols-[65fr_35fr] md:grid-rows-2 gap-0.5 bg-border">
        {items.map((article, i) => (
          <Link
            key={article.id}
            href={`/news/${article.slug}`}
            className={`relative overflow-hidden bg-bg3 cursor-pointer group block ${
              i === 0 ? 'md:row-span-2 min-h-[420px]' : 'min-h-[200px]'
            }`}
          >
            {/* Background: real image or gradient fallback */}
            {article.image_url ? (
              <img
                src={article.image_url}
                alt={article.title}
                className="absolute inset-0 w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-med"
              />
            ) : (
              <div
                className="absolute inset-0 group-hover:scale-[1.03] transition-transform duration-med"
                style={{ background: gradients[i] || gradients[0] }}
              />
            )}

            {/* Text overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-5 md:p-6 bg-gradient-to-t from-black/80 to-transparent z-10">
              <p className="font-condensed text-xs font-semibold uppercase tracking-wide text-white/75 mb-1.5">
                {article.category}
              </p>
              <h3
                className={`font-condensed font-bold text-white uppercase leading-tight line-clamp-3 ${
                  i === 0 ? 'text-3xl md:text-[30px]' : 'text-xl'
                }`}
              >
                {article.title}
              </h3>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
