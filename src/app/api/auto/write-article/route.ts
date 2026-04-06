import { NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'
import { createClient } from '@supabase/supabase-js'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)

export async function POST(req: Request) {
  const { topic, category, keywords } = await req.json()
  const secret = req.headers.get('x-api-secret')
  if (secret !== process.env.SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const message = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2000,
    messages: [{
      role: 'user',
      content: `Write a pickleball news article.
Topic: ${topic}
Category: ${category}
Keywords: ${keywords || 'pickleball'}

Return JSON only:
{
  "title": "SEO-optimized title",
  "slug": "url-friendly-slug",
  "excerpt": "1-2 sentence summary",
  "content": "<p>Full HTML article 300-400 words</p>",
  "meta_description": "SEO meta description 150 chars"
}`
    }]
  })

  const text = (message.content[0] as { type: 'text'; text: string }).text
  const article = JSON.parse(text.replace(/```json|```/g, '').trim())

  const { data, error } = await supabase.from('articles').insert({
    title: article.title,
    slug: article.slug,
    category,
    excerpt: article.excerpt,
    content: article.content,
    published_at: new Date().toISOString(),
    is_featured: false,
    views: 0,
  }).select()

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json({ ok: true, article: data?.[0] })
}
