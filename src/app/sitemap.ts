import type { MetadataRoute } from 'next'
import { getArticles, getPaddles, getPlayers } from '@/lib/supabase'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = 'https://picklrlab.com'

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: base, changeFrequency: 'daily', priority: 1.0 },
    { url: `${base}/news`, changeFrequency: 'hourly', priority: 0.9 },
    { url: `${base}/rankings`, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/reviews`, changeFrequency: 'weekly', priority: 0.8 },
    { url: `${base}/players`, changeFrequency: 'weekly', priority: 0.7 },
    { url: `${base}/tournaments`, changeFrequency: 'weekly', priority: 0.7 },
    { url: `${base}/courts`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/tools`, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${base}/tools/brackets`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/tools/drills`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/tools/elo`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/about`, changeFrequency: 'monthly', priority: 0.4 },
  ]

  // Dynamic pages
  const [articles, paddles, players] = await Promise.all([
    getArticles(undefined, 200),
    getPaddles(),
    getPlayers(),
  ])

  const articlePages: MetadataRoute.Sitemap = articles.map(a => ({
    url: `${base}/news/${a.slug}`,
    lastModified: a.published_at ? new Date(a.published_at) : undefined,
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const reviewPages: MetadataRoute.Sitemap = paddles.map(p => ({
    url: `${base}/reviews/${p.slug}`,
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }))

  const playerPages: MetadataRoute.Sitemap = players.map(p => ({
    url: `${base}/players/${p.slug}`,
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }))

  return [...staticPages, ...articlePages, ...reviewPages, ...playerPages]
}
