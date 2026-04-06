'use client'

import { useEffect } from 'react'

export default function ArticleViewCounter({ articleId }: { articleId: string }) {
  useEffect(() => {
    // POST view count increment on client side
    fetch('/api/health', { method: 'GET' }).catch(() => {})
    // In production, this would POST to an article views endpoint
  }, [articleId])

  return null
}
