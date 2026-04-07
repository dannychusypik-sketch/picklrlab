import { createClient } from '@supabase/supabase-js'
import type { Ranking, Paddle, Article, Match, Court, Player, Tournament } from './types'
import {
  seedPlayers, seedRankings, seedPaddles, seedArticles, seedMatches, seedMostRead, seedTournaments,
} from './seed-data'
import { cached } from './redis'

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

const isPlaceholder = !url || url.includes('placeholder')
const hasRedis = !!process.env.UPSTASH_REDIS_URL

export const supabase = createClient(
  isPlaceholder ? 'https://placeholder.supabase.co' : url,
  isPlaceholder ? 'placeholder' : key,
)

// Helper: wrap with cache if Redis available, otherwise direct fetch
function withCache<T>(key: string, fetcher: () => Promise<T>, ttl?: number): Promise<T> {
  if (!hasRedis) return fetcher()
  return cached(key, fetcher, ttl)
}

// ---- Rankings ------------------------------------------------
export async function getRankings(category: string): Promise<Ranking[]> {
  if (isPlaceholder) return seedRankings.filter(r => r.category === category)
  return withCache(`rankings:${category}`, async () => {
    const { data } = await supabase
      .from('rankings')
      .select('*, player:players(name, country, sponsor, paddle, photo_url, slug)')
      .eq('category', category)
      .order('rank')
    return data ?? []
  }, 600) // 10 min cache
}

export async function getAllRankings(): Promise<Ranking[]> {
  if (isPlaceholder) return seedRankings
  return withCache('rankings:all', async () => {
    const { data } = await supabase
      .from('rankings')
      .select('*, player:players(name, country, sponsor, paddle, photo_url, slug)')
      .order('rank')
    return data ?? []
  }, 600)
}

// ---- Paddles -------------------------------------------------
export async function getPaddles(): Promise<Paddle[]> {
  if (isPlaceholder) return seedPaddles
  return withCache('paddles:all', async () => {
    const { data } = await supabase
      .from('paddles')
      .select('*')
      .order('score_overall', { ascending: false })
    return data ?? []
  }, 3600) // 1 hour cache
}

export async function getPaddleBySlug(slug: string): Promise<Paddle | null> {
  if (isPlaceholder) return seedPaddles.find(p => p.slug === slug) ?? null
  return withCache(`paddle:${slug}`, async () => {
    const { data } = await supabase
      .from('paddles')
      .select('*')
      .eq('slug', slug)
      .single()
    return data
  }, 3600)
}

export async function getFeaturedPaddles(): Promise<Paddle[]> {
  if (isPlaceholder) return seedPaddles.filter(p => p.featured).slice(0, 3)
  return withCache('paddles:featured', async () => {
    const { data } = await supabase
      .from('paddles')
      .select('*')
      .eq('featured', true)
      .order('score_overall', { ascending: false })
      .limit(3)
    return data ?? []
  }, 3600)
}

// ---- Articles ------------------------------------------------
export async function getArticles(category?: string, limit = 20): Promise<Article[]> {
  if (isPlaceholder) {
    let arts = seedArticles
    if (category) arts = arts.filter(a => a.category === category)
    return arts.slice(0, limit)
  }
  return withCache(`articles:${category || 'all'}:${limit}`, async () => {
    let q = supabase
      .from('articles')
      .select('id,title,slug,category,excerpt,author,published_at,views,is_featured,image_url')
      .not('published_at', 'is', null)
      .order('published_at', { ascending: false })
      .limit(limit)
    if (category) q = q.eq('category', category)
    const { data } = await q
    return data ?? []
  }, 300) // 5 min cache
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
  if (isPlaceholder) return seedArticles.find(a => a.slug === slug) ?? null
  return withCache(`article:${slug}`, async () => {
    const { data } = await supabase
      .from('articles')
      .select('*')
      .eq('slug', slug)
      .single()
    return data
  }, 600)
}

export async function getFeaturedArticles(limit = 5): Promise<Article[]> {
  if (isPlaceholder) return seedArticles.filter(a => a.is_featured).slice(0, limit)
  return withCache(`articles:featured:${limit}`, async () => {
    const { data } = await supabase
      .from('articles')
      .select('id,title,slug,category,excerpt,author,published_at,views,is_featured,image_url')
      .eq('is_featured', true)
      .not('published_at', 'is', null)
      .order('published_at', { ascending: false })
      .limit(limit)
    return data ?? []
  }, 300)
}

export async function getHotArticles(limit = 5): Promise<Article[]> {
  if (isPlaceholder) return seedArticles.filter(a => a.is_featured && a.category !== 'training').slice(0, limit)
  return withCache('articles:hot:' + limit, async () => {
    const { data } = await supabase
      .from('articles')
      .select('id,title,slug,category,excerpt,author,published_at,views,is_featured,image_url')
      .not('published_at', 'is', null)
      .neq('category', 'training')
      .order('views', { ascending: false })
      .limit(limit)
    return data ?? []
  }, 300)
}

export async function getMostReadArticles(limit = 5): Promise<Pick<Article, 'id' | 'title' | 'slug' | 'category' | 'views'>[]> {
  if (isPlaceholder) return seedMostRead.slice(0, limit)
  return withCache(`articles:mostread:${limit}`, async () => {
    const { data } = await supabase
      .from('articles')
      .select('id,title,slug,category,views')
      .not('published_at', 'is', null)
      .order('views', { ascending: false })
      .limit(limit)
    return data ?? []
  }, 300)
}

// ---- Live Matches (short cache - 60s) ------------------------
export async function getLiveMatches(): Promise<Match[]> {
  if (isPlaceholder) return seedMatches
  return withCache('matches:live', async () => {
    const { data } = await supabase
      .from('matches')
      .select(`
        *,
        player1:players!player1_id(name, country),
        player2:players!player2_id(name, country)
      `)
      .in('status', ['live', 'upcoming', 'done'])
      .order('scheduled_at')
      .limit(6)
    return data ?? []
  }, 60) // 1 min cache for live data
}

// ---- Players -------------------------------------------------
export async function getPlayers(): Promise<Player[]> {
  if (isPlaceholder) return seedPlayers
  return withCache('players:all', async () => {
    const { data } = await supabase
      .from('players')
      .select('*')
      .order('name')
    return data ?? []
  }, 1800) // 30 min cache
}

export async function getPlayerBySlug(slug: string): Promise<Player | null> {
  if (isPlaceholder) return seedPlayers.find(p => p.slug === slug) ?? null
  return withCache(`player:${slug}`, async () => {
    const { data } = await supabase
      .from('players')
      .select('*')
      .eq('slug', slug)
      .single()
    return data
  }, 1800)
}

// ---- Courts --------------------------------------------------
export async function getCourts(): Promise<Court[]> {
  if (isPlaceholder) return []
  return withCache('courts:all', async () => {
    const { data } = await supabase
      .from('courts')
      .select('*')
      .order('name')
    return data ?? []
  }, 3600)
}

// ---- Tournaments ---------------------------------------------
export async function getTournaments(): Promise<Tournament[]> {
  if (isPlaceholder) return seedTournaments
  return withCache('tournaments:all', async () => {
    const { data } = await supabase
      .from('tournaments')
      .select('*')
      .order('start_date', { ascending: false })
    return data ?? []
  }, 1800)
}

export async function getTournamentBySlug(slug: string): Promise<Tournament | null> {
  if (isPlaceholder) return seedTournaments.find(t => t.slug === slug) ?? null
  return withCache(`tournament:${slug}`, async () => {
    const { data } = await supabase
      .from('tournaments')
      .select('*')
      .eq('slug', slug)
      .single()
    return data
  }, 1800)
}
