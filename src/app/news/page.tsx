import type { Metadata } from 'next'
import Link from 'next/link'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import SectionHeader from '@/components/ui/SectionHeader'
import NewsFilter from '@/components/news/NewsFilter'
import { getArticles, getMostReadArticles } from '@/lib/supabase'

export const metadata: Metadata = {
  title: 'News',
}

export default async function NewsPage() {
  const [articles, mostRead] = await Promise.all([
    getArticles(undefined, 50),
    getMostReadArticles(),
  ])

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          STORIES
        </h1>

        <div className="mt-6">
          <NewsFilter articles={articles} />
        </div>

        {/* Most Read */}
        <div className="mt-12">
          <SectionHeader title="Most Read" />
          <ol className="mt-4 space-y-3">
            {mostRead.map((article, i) => (
              <li key={article.id} className="flex items-start gap-3">
                <span className="font-condensed text-2xl font-bold text-ink5 w-8 shrink-0">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <div>
                  <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                    {article.category}
                  </span>
                  <Link
                    href={`/news/${article.slug}`}
                    className="block font-condensed text-md font-bold uppercase leading-tight mt-0.5 hover:text-blue transition-colors"
                  >
                    {article.title}
                  </Link>
                  <span className="text-xs text-ink4">{article.views?.toLocaleString()} views</span>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </main>
      <Footer />
    </>
  )
}
