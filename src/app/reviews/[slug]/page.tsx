import type { Metadata } from 'next'
import Link from 'next/link'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import { getPaddles, getPaddleBySlug } from '@/lib/supabase'
import { ProductSchema } from '@/components/seo/JsonLd'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  const paddles = await getPaddles()
  return paddles.map((p) => ({ slug: p.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const paddle = await getPaddleBySlug(slug)
  if (!paddle) return { title: 'Review Not Found' }
  return {
    title: `${paddle.brand} ${paddle.name} Review`,
    description: paddle.verdict ?? undefined,
  }
}

function ScoreBar({ label, score }: { label: string; score?: number }) {
  const value = score ?? 0
  const pct = Math.min(100, value)
  return (
    <div className="flex items-center gap-3">
      <span className="font-condensed text-xs font-bold uppercase tracking-wider w-24 shrink-0">
        {label}
      </span>
      <div className="flex-1 h-3 bg-bg3 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue to-navy rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="font-condensed text-sm font-bold w-8 text-right">{value}</span>
    </div>
  )
}

export default async function ReviewDetailPage({ params }: Props) {
  const { slug } = await params
  const paddle = await getPaddleBySlug(slug)

  if (!paddle) {
    return (
      <>
        <Nav />
        <main className="max-w-site mx-auto px-5 py-20 text-center">
          <h1 className="font-condensed text-3xl font-bold uppercase">Review Not Found</h1>
          <Link href="/reviews" className="text-blue mt-4 inline-block hover:underline">
            Back to Reviews
          </Link>
        </main>
        <Footer />
      </>
    )
  }

  const allPaddles = await getPaddles()
  const related = allPaddles.filter((p) => p.id !== paddle.id && p.brand === paddle.brand).slice(0, 3)

  return (
    <>
      <ProductSchema paddle={paddle} />
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs text-ink4 mb-6">
          <Link href="/" className="hover:text-blue">Home</Link>
          <span>/</span>
          <Link href="/reviews" className="hover:text-blue">Reviews</Link>
          <span>/</span>
          <span className="text-ink3">{paddle.brand} {paddle.name}</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="lg:col-span-2">
            {/* Hero */}
            <div className="flex items-start gap-6">
              {/* Score circle */}
              <div className="w-24 h-24 shrink-0 rounded-full bg-gradient-to-br from-navy to-blue flex items-center justify-center">
                <span className="font-condensed text-4xl font-bold text-white">
                  {paddle.score_overall ?? '-'}
                </span>
              </div>
              <div>
                <span className="font-condensed text-xs font-bold uppercase tracking-wider text-blue">
                  {paddle.brand}
                </span>
                <h1 className="font-condensed text-3xl font-bold uppercase leading-tight mt-1">
                  {paddle.name}
                </h1>
                {paddle.price_usd && (
                  <p className="text-lg font-bold mt-2">${paddle.price_usd}</p>
                )}
              </div>
            </div>

            {/* Verdict */}
            <div className="mt-6 p-4 bg-bg2 rounded-lg">
              <h3 className="font-condensed text-sm font-bold uppercase tracking-wider mb-1">
                Verdict
              </h3>
              <p className="text-base text-ink2">{paddle.verdict}</p>
            </div>

            {/* 6 Score bars */}
            <div className="mt-6 space-y-3">
              <ScoreBar label="Control" score={paddle.score_control} />
              <ScoreBar label="Power" score={paddle.score_power} />
              <ScoreBar label="Spin" score={paddle.score_spin} />
              <ScoreBar label="Durability" score={paddle.score_durability} />
              <ScoreBar label="Feel" score={paddle.score_feel} />
              <ScoreBar label="Value" score={paddle.score_value} />
            </div>

            {/* Good / Bad */}
            <div className="mt-6 grid grid-cols-2 gap-4">
              {paddle.good_for && paddle.good_for.length > 0 && (
                <div>
                  <h3 className="font-condensed text-sm font-bold uppercase tracking-wider text-green2 mb-2">
                    Good For
                  </h3>
                  <ul className="space-y-1">
                    {paddle.good_for.map((g) => (
                      <li key={g} className="text-sm text-ink2 flex items-center gap-2">
                        <span className="text-green2">+</span> {g}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {paddle.bad_for && paddle.bad_for.length > 0 && (
                <div>
                  <h3 className="font-condensed text-sm font-bold uppercase tracking-wider text-red mb-2">
                    Not Ideal For
                  </h3>
                  <ul className="space-y-1">
                    {paddle.bad_for.map((b) => (
                      <li key={b} className="text-sm text-ink2 flex items-center gap-2">
                        <span className="text-red">-</span> {b}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar: Specs + Buy */}
          <div>
            <div className="border border-border rounded-lg p-4 sticky top-20">
              <h3 className="font-condensed text-sm font-bold uppercase tracking-wider mb-3">
                Specifications
              </h3>
              <div className="space-y-2 text-sm">
                {paddle.core_mm && (
                  <div className="flex justify-between">
                    <span className="text-ink4">Core Thickness</span>
                    <span className="font-semibold">{paddle.core_mm}mm</span>
                  </div>
                )}
                {paddle.face_material && (
                  <div className="flex justify-between">
                    <span className="text-ink4">Face</span>
                    <span className="font-semibold">{paddle.face_material}</span>
                  </div>
                )}
                {paddle.weight_oz && (
                  <div className="flex justify-between">
                    <span className="text-ink4">Weight</span>
                    <span className="font-semibold">{paddle.weight_oz} oz</span>
                  </div>
                )}
                {paddle.length_in && (
                  <div className="flex justify-between">
                    <span className="text-ink4">Length</span>
                    <span className="font-semibold">{paddle.length_in}&quot;</span>
                  </div>
                )}
                {paddle.width_in && (
                  <div className="flex justify-between">
                    <span className="text-ink4">Width</span>
                    <span className="font-semibold">{paddle.width_in}&quot;</span>
                  </div>
                )}
              </div>

              {paddle.buy_url && (
                <a
                  href={paddle.buy_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full text-center font-condensed text-sm font-bold uppercase tracking-wide bg-blue text-white py-3 rounded-lg mt-4 hover:bg-blue-hover transition-colors"
                >
                  Buy Now {paddle.price_usd && `— $${paddle.price_usd}`}
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Related paddles */}
        {related.length > 0 && (
          <div className="mt-12 border-t border-border pt-8">
            <h2 className="font-condensed text-lg font-bold uppercase tracking-wide mb-4">
              More from {paddle.brand}
            </h2>
            <div className="flex flex-wrap gap-4">
              {related.map((p) => (
                <Link
                  key={p.id}
                  href={`/reviews/${p.slug}`}
                  className="flex gap-3 p-3 border border-border rounded-lg hover:shadow-md transition-shadow w-[300px]"
                >
                  <div className="w-12 h-12 shrink-0 rounded-lg bg-gradient-to-br from-navy to-blue flex items-center justify-center">
                    <span className="font-condensed text-lg font-bold text-white">
                      {p.score_overall ?? '-'}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-condensed text-sm font-bold uppercase">{p.name}</h3>
                    <p className="text-xs text-ink4 mt-0.5">${p.price_usd}</p>
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
