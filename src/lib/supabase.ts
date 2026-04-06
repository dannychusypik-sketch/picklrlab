import { createClient } from '@supabase/supabase-js'
import type { Ranking, Paddle, Article, Match, Court, Player, Tournament } from './types'
import {
  seedPlayers, seedRankings, seedPaddles, seedArticles, seedMatches, seedMostRead, seedTournaments,
} from './seed-data'

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

const isPlaceholder = !url || url.includes('placeholder')

export const supabase = createClient(
  isPlaceholder ? 'https://placeholder.supabase.co' : url,
  isPlaceholder ? 'placeholder' : key,
)

// ---- Rankings ------------------------------------------------
export async function getRankings(category: string): Promise<Ranking[]> {
  if (isPlaceholder) return seedRankings.filter(r => r.category === category)
  const { data } = await supabase
    .from('rankings')
    .select('*, player:players(name, country, sponsor, paddle, photo_url, slug)')
    .eq('category', category)
    .order('rank')
  return data ?? []
}

// ---- Paddles -------------------------------------------------
export async function getPaddles(): Promise<Paddle[]> {
  if (isPlaceholder) return seedPaddles
  const { data } = await supabase
    .from('paddles')
    .select('*')
    .order('score_overall', { ascending: false })
  return data ?? []
}

export async function getPaddleBySlug(slug: string): Promise<Paddle | null> {
  if (isPlaceholder) return seedPaddles.find(p => p.slug === slug) ?? null
  const { data } = await supabase
    .from('paddles')
    .select('*')
    .eq('slug', slug)
    .single()
  return data
}

export async function getFeaturedPaddles(): Promise<Paddle[]> {
  if (isPlaceholder) return seedPaddles.filter(p => p.featured).slice(0, 3)
  const { data } = await supabase
    .from('paddles')
    .select('*')
    .eq('featured', true)
    .order('score_overall', { ascending: false })
    .limit(3)
  return data ?? []
}

// ---- Articles ------------------------------------------------
export async function getArticles(category?: string, limit = 20): Promise<Article[]> {
  if (isPlaceholder) {
    let arts = seedArticles
    if (category) arts = arts.filter(a => a.category === category)
    return arts.slice(0, limit)
  }
  let q = supabase
    .from('articles')
    .select('id,title,slug,category,excerpt,author,published_at,views,is_featured')
    .not('published_at', 'is', null)
    .order('published_at', { ascending: false })
    .limit(limit)
  if (category) q = q.eq('category', category)
  const { data } = await q
  return data ?? []
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
  if (isPlaceholder) return seedArticles.find(a => a.slug === slug) ?? null
  const { data } = await supabase
    .from('articles')
    .select('*')
    .eq('slug', slug)
    .single()
  return data
}

export async function getFeaturedArticles(limit = 5): Promise<Article[]> {
  if (isPlaceholder) return seedArticles.filter(a => a.is_featured).slice(0, limit)
  const { data } = await supabase
    .from('articles')
    .select('id,title,slug,category,excerpt,author,published_at,views,is_featured')
    .eq('is_featured', true)
    .not('published_at', 'is', null)
    .order('published_at', { ascending: false })
    .limit(limit)
  return data ?? []
}

export async function getMostReadArticles(limit = 5): Promise<Pick<Article, 'id' | 'title' | 'slug' | 'category' | 'views'>[]> {
  if (isPlaceholder) return seedMostRead.slice(0, limit)
  const { data } = await supabase
    .from('articles')
    .select('id,title,slug,category,views')
    .not('published_at', 'is', null)
    .order('views', { ascending: false })
    .limit(limit)
  return data ?? []
}

// ---- Live Matches --------------------------------------------
export async function getLiveMatches(): Promise<Match[]> {
  if (isPlaceholder) return seedMatches
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
}

// ---- Players -------------------------------------------------
export async function getPlayers(): Promise<Player[]> {
  if (isPlaceholder) return seedPlayers
  const { data } = await supabase
    .from('players')
    .select('*')
    .order('name')
  return data ?? []
}

export async function getPlayerBySlug(slug: string): Promise<Player | null> {
  if (isPlaceholder) return seedPlayers.find(p => p.slug === slug) ?? null
  const { data } = await supabase
    .from('players')
    .select('*')
    .eq('slug', slug)
    .single()
  return data
}

// ---- Courts --------------------------------------------------
export async function getCourts(): Promise<Court[]> {
  if (isPlaceholder) return []
  const { data } = await supabase
    .from('courts')
    .select('*')
    .order('name')
  return data ?? []
}

// ---- Tournaments ---------------------------------------------
export async function getTournaments(): Promise<Tournament[]> {
  if (isPlaceholder) return seedTournaments
  const { data } = await supabase
    .from('tournaments')
    .select('*')
    .order('start_date', { ascending: false })
  return data ?? []
}

export async function getTournamentBySlug(slug: string): Promise<Tournament | null> {
  if (isPlaceholder) return seedTournaments.find(t => t.slug === slug) ?? null
  const { data } = await supabase
    .from('tournaments')
    .select('*')
    .eq('slug', slug)
    .single()
  return data
}
