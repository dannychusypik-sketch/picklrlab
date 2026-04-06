import type { Metadata } from 'next'
import Link from 'next/link'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import { getArticles, getArticleBySlug } from '@/lib/supabase'
import ArticleViewCounter from '@/components/news/ArticleViewCounter'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  const articles = await getArticles(undefined, 50)
  return articles.map((a) => ({ slug: a.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const article = await getArticleBySlug(slug)
  if (!article) return { title: 'Article Not Found' }
  return {
    title: article.title,
    description: article.excerpt ?? undefined,
  }
}

function estimateReadTime(content?: string): number {
  if (!content) return 1
  const words = content.replace(/<[^>]+>/g, '').split(/\s+/).length
  return Math.max(1, Math.ceil(words / 200))
}

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params
  const article = await getArticleBySlug(slug)

  if (!article) {
    return (
      <>
        <Nav />
        <main className="max-w-site mx-auto px-5 py-20 text-center">
          <h1 className="font-condensed text-3xl font-bold uppercase">Article Not Found</h1>
          <Link href="/news" className="text-blue mt-4 inline-block hover:underline">
            Back to News
          </Link>
        </main>
        <Footer />
      </>
    )
  }

  const readTime = estimateReadTime(article.content)
  const allArticles = await getArticles(undefined, 50)
  const related = allArticles
    .filter((a) => a.id !== article.id && a.category === article.category)
    .slice(0, 3)

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs text-ink4 mb-6">
          <Link href="/" className="hover:text-blue">Home</Link>
          <span>/</span>
          <Link href="/news" className="hover:text-blue">News</Link>
          <span>/</span>
          <span className="text-ink3">{article.category}</span>
        </nav>

        <article className="max-w-[720px]">
          <span className="font-condensed text-xs font-bold uppercase tracking-wider text-blue">
            {article.category}
          </span>
          <h1 className="font-condensed text-3xl font-bold uppercase leading-tight mt-2">
            {article.title}
          </h1>

          <div className="flex items-center gap-4 mt-4 text-xs text-ink4">
            <span>By {article.author}</span>
            {article.published_at && (
              <span>
                {new Date(article.published_at).toLocaleDateString('en-US', {
                  month: 'long', day: 'numeric', year: 'numeric',
                })}
              </span>
            )}
            <span>{readTime} min read</span>
            <span>{article.views?.toLocaleString()} views</span>
          </div>

          {/* Share buttons */}
          <div className="flex items-center gap-3 mt-4 pb-4 border-b border-border">
            <span className="text-xs text-ink4 font-semibold uppercase">Share:</span>
            <a
              href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title)}&url=${encodeURIComponent(`https://picklrlab.com/news/${article.slug}`)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-ink3 hover:text-blue transition text-sm"
            >
              Twitter
            </a>
            <a
              href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(`https://picklrlab.com/news/${article.slug}`)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-ink3 hover:text-blue transition text-sm"
            >
              Facebook
            </a>
          </div>

          {/* Content */}
          {article.content ? (
            <div
              className="mt-6 text-[17px] leading-relaxed prose prose-neutral max-w-none"
              dangerouslySetInnerHTML={{ __html: article.content }}
            />
          ) : (
            <p className="mt-6 text-[17px] leading-relaxed text-ink3">
              {article.excerpt}
            </p>
          )}
        </article>

        {/* View counter (client side) */}
        <ArticleViewCounter articleId={article.id} />

        {/* Related articles */}
        {related.length > 0 && (
          <div className="mt-12 border-t border-border pt-8">
            <h2 className="font-condensed text-lg font-bold uppercase tracking-wide mb-4">
              Related Stories
            </h2>
            <div className="flex flex-wrap gap-4">
              {related.map((r) => (
                <Link
                  key={r.id}
                  href={`/news/${r.slug}`}
                  className="w-[300px] bg-white border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-fast"
                >
                  <div className="h-[140px] bg-gradient-to-br from-navy via-blue to-ink" />
                  <div className="p-3">
                    <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                      {r.category}
                    </span>
                    <h3 className="font-condensed text-sm font-bold uppercase leading-tight mt-1 line-clamp-3">
                      {r.title}
                    </h3>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </>
  )
}
