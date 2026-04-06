export const SITE_NAME = 'PicklrLab'
export const SITE_TAGLINE = 'Global Authority'
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://picklrlab.com'
export const SITE_EMAIL = 'hello@picklrlab.com'

export const RANKING_CATEGORIES = [
  { key: 'mens_singles', label: "Men's Singles" },
  { key: 'womens_singles', label: "Women's Singles" },
  { key: 'mens_doubles', label: "Men's Doubles" },
  { key: 'womens_doubles', label: "Women's Doubles" },
  { key: 'mixed_doubles', label: 'Mixed Doubles' },
  { key: 'vn', label: 'Vietnam' },
  { key: 'sea', label: 'Southeast Asia' },
] as const

export const NEWS_CATEGORIES = [
  { key: 'all', label: 'All' },
  { key: 'tournament', label: 'Tournaments' },
  { key: 'review', label: 'Reviews' },
  { key: 'rankings', label: 'Rankings' },
  { key: 'sea', label: 'SEA' },
  { key: 'vietnam', label: 'Vietnam' },
  { key: 'gear', label: 'Gear' },
  { key: 'training', label: 'Training' },
  { key: 'opinion', label: 'Opinion' },
  { key: 'video', label: 'Video' },
] as const

export const SPORT_BANNERS = {
  ppa: { label: 'PPA TOUR', color: 'var(--navy)' },
  rankings: { label: 'WORLD RANKINGS', color: 'var(--green2)' },
  reviews: { label: 'LAB REVIEWS', color: 'var(--red)' },
  news: { label: 'LATEST NEWS', color: '#111' },
} as const
