import { getPaddles, getArticles, getHotArticles, getLiveMatches, getRankings, getMostReadArticles } from '@/lib/supabase'
import { WebsiteSchema } from '@/components/seo/JsonLd'
import Ticker from '@/components/layout/Ticker'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import ScoresBar from '@/components/home/ScoresBar'
import FeaturedStories from '@/components/home/FeaturedStories'
import MoreStories from '@/components/home/MoreStories'
import VideoHighlights from '@/components/home/VideoHighlights'
import HomeRankings from '@/components/home/HomeRankings'
import HomeReviews from '@/components/home/HomeReviews'
import HomeNews from '@/components/home/HomeNews'
import Newsletter from '@/components/home/Newsletter'
import SectionHeader from '@/components/ui/SectionHeader'
import SportBanner from '@/components/ui/SportBanner'
import Link from 'next/link'

export default async function Home() {
  const [paddles, articles, hotArticles, mostReadArticles, matches, rankings, trainingArticles] = await Promise.all([
    getPaddles(),
    getArticles(undefined, 20),
    getHotArticles(5),
    getMostReadArticles(5),
    getLiveMatches(),
    getRankings('mens_singles'),
    getArticles('training', 6),
  ])

  const moreStories = articles.filter(a => !a.is_featured).slice(0, 6)

  return (
    <>
      <WebsiteSchema />
      <Ticker />
      <Nav />
      <ScoresBar matches={matches} />

      {/* Featured Stories */}
      <div className="max-w-site mx-auto px-5">
        <SectionHeader title="Featured Stories" />
      </div>
      <FeaturedStories articles={hotArticles} />

      {/* More Stories */}
      <div className="max-w-site mx-auto px-5">
        <SectionHeader title="More Stories" href="/news" linkText="View All Stories →" />
      </div>
      <MoreStories articles={moreStories} />

      {/* Rankings */}
      <SportBanner label="WORLD RANKINGS" color="#0a5c36" />
      <HomeRankings rankings={rankings} />

      {/* Reviews */}
      <SportBanner label="LAB REVIEWS" color="#d0021b" />
      <HomeReviews paddles={paddles} />

      {/* Video Highlights */}
      <VideoHighlights />

      {/* Latest News */}
      <SportBanner label="LATEST NEWS" color="#000000" />
      <HomeNews articles={articles} mostRead={mostReadArticles} />

      {/* Training & Tips */}
      {trainingArticles.length > 0 && (
        <>
          <SportBanner label="TRAINING & TIPS" color="#0059b5" />
          <div className="max-w-site mx-auto px-5 py-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {trainingArticles.map(article => (
                <Link key={article.id} href={`/news/${article.slug}`} className="group block bg-bg2 rounded overflow-hidden hover:shadow-md transition-shadow">
                  {article.image_url ? (
                    <img src={article.image_url} alt={article.title} className="w-full h-40 object-cover" />
                  ) : (
                    <div className="w-full h-40 bg-gradient-to-br from-blue to-navy flex items-center justify-center">
                      <span className="text-white/30 text-5xl font-condensed font-bold">TIPS</span>
                    </div>
                  )}
                  <div className="p-4">
                    <h3 className="font-body text-md font-bold leading-snug group-hover:text-blue line-clamp-2">{article.title}</h3>
                    {article.excerpt && (
                      <p className="text-xs text-ink4 mt-1.5 line-clamp-2">{article.excerpt}</p>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Newsletter + Footer */}
      <Newsletter />
      <Footer />
    </>
  )
}
