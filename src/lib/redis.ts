import { Redis } from '@upstash/redis'

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!,
})

const DEFAULT_TTL = 300 // 5 minutes

/**
 * Cache wrapper: check Redis first, fallback to fetcher, store result
 */
export async function cached<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = DEFAULT_TTL
): Promise<T> {
  try {
    const hit = await redis.get<T>(key)
    if (hit !== null && hit !== undefined) {
      return hit
    }
  } catch {
    // Redis down — just fetch directly
  }

  const data = await fetcher()

  try {
    await redis.set(key, JSON.stringify(data), { ex: ttl })
  } catch {
    // Redis write failed — ignore
  }

  return data
}

/**
 * Invalidate cache by key pattern
 */
export async function invalidateCache(pattern: string): Promise<void> {
  try {
    const keys = await redis.keys(pattern)
    if (keys.length > 0) {
      await redis.del(...keys)
    }
  } catch {
    // Ignore
  }
}
