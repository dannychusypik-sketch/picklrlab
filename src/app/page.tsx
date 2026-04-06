import { getPaddles, getArticles, getFeaturedArticles, getLiveMatches, getRankings, getMostReadArticles } from '@/lib/supabase'
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

export default async function Home() {
  const [paddles, articles, featuredArticles, mostReadArticles, matches, rankings] = await Promise.all([
    getPaddles(),
    getArticles(undefined, 20),
    getFeaturedArticles(5),
    getMostReadArticles(5),
    getLiveMatches(),
    getRankings('mens_singles'),
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
      <FeaturedStories articles={featuredArticles} />

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

      {/* Newsletter + Footer */}
      <Newsletter />
      <Footer />
    </>
  )
}
