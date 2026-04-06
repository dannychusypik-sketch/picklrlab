import type { Metadata } from 'next'
import Link from 'next/link'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
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

  const featuredArticle = articles.find((a) => a.is_featured) || articles[0]

  return (
    <>
      <Nav />

      {/* Hero: Featured Article */}
      {featuredArticle && (
        <section className="relative w-full h-[420px] md:h-[480px] overflow-hidden">
          {featuredArticle.image_url ? (
            <img
              src={featuredArticle.image_url}
              alt={featuredArticle.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-navy via-blue to-ink" />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10 max-w-site mx-auto">
            <span className="inline-block bg-red text-white font-condensed text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-sm mb-3">
              {featuredArticle.category}
            </span>
            <Link href={`/news/${featuredArticle.slug}`}>
              <h1 className="font-condensed text-3xl md:text-4xl font-bold text-white uppercase leading-tight max-w-3xl hover:text-white/90 transition-colors">
                {featuredArticle.title}
              </h1>
            </Link>
            {featuredArticle.excerpt && (
              <p className="text-white/80 text-sm md:text-base mt-3 max-w-2xl line-clamp-2">
                {featuredArticle.excerpt}
              </p>
            )}
            <div className="flex items-center gap-3 mt-3 text-white/60 text-xs">
              <span>By {featuredArticle.author}</span>
              {featuredArticle.published_at && (
                <span>
                  {new Date(featuredArticle.published_at).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </span>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Main Content */}
      <main className="max-w-site mx-auto px-5 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
          {/* Left: Articles with filter */}
          <div>
            <NewsFilter articles={articles} featuredId={featuredArticle?.id} />
          </div>

          {/* Right Sidebar */}
          <aside className="space-y-8">
            {/* Most Read */}
            <div>
              <h3 className="font-condensed text-lg font-bold uppercase tracking-tight border-b-2 border-red pb-2 mb-3">
                Most Read
              </h3>
              <ol className="space-y-0">
                {mostRead.map((article, i) => (
                  <li key={article.id} className="border-l-2 border-red/20 hover:border-red transition-colors">
                    <Link
                      href={`/news/${article.slug}`}
                      className="group flex items-start gap-3 py-3 px-3 hover:bg-bg2 transition-colors"
                    >
                      <span className="font-condensed text-2xl font-bold text-red/40 leading-none mt-0.5 w-6 shrink-0">
                        {i + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="font-body text-sm font-bold leading-snug group-hover:text-blue transition-colors">
                          {article.title}
                        </p>
                        <p className="text-2xs text-ink4 mt-1">
                          {article.views?.toLocaleString()} views
                        </p>
                      </div>
                    </Link>
                  </li>
                ))}
              </ol>
            </div>

            {/* Newsletter Signup */}
            <div className="bg-gradient-to-br from-navy to-blue rounded-lg p-5 text-white">
              <h3 className="font-condensed text-lg font-bold uppercase">Stay Updated</h3>
              <p className="text-white/70 text-xs mt-1">Get the latest pickleball news delivered to your inbox.</p>
              <div className="mt-3 space-y-2">
                <input
                  type="email"
                  placeholder="Your email address"
                  className="w-full px-3 py-2 rounded text-sm text-ink bg-white/95 placeholder:text-ink4 outline-none focus:ring-2 focus:ring-white/50"
                />
                <button className="w-full font-condensed text-sm font-bold uppercase tracking-wide bg-red hover:bg-red/90 text-white px-4 py-2 rounded transition-colors">
                  Subscribe
                </button>
              </div>
            </div>

            {/* Popular Tags */}
            <div>
              <h3 className="font-condensed text-lg font-bold uppercase tracking-tight border-b-2 border-ink pb-2 mb-3">
                Popular Tags
              </h3>
              <div className="flex flex-wrap gap-2 mt-3">
                {['Tournaments', 'Reviews', 'Rankings', 'Training', 'Gear', 'SEA', 'Vietnam', 'Opinion'].map((tag) => (
                  <span
                    key={tag}
                    className="font-condensed text-xs font-semibold uppercase tracking-wide bg-bg2 text-ink3 px-3 py-1.5 rounded-pill hover:bg-bg3 cursor-pointer transition-colors"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </main>

      <Footer />
    </>
  )
}
