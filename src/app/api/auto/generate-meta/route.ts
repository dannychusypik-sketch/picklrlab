import { NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'
import { createClient } from '@supabase/supabase-js'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)

export async function POST(req: Request) {
  const secret = req.headers.get('x-api-secret')
  if (secret !== process.env.SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { article_id } = await req.json()

  // Fetch article(s) — single article or all without excerpt
  let query = supabase.from('articles').select('*')
  if (article_id) {
    query = query.eq('id', article_id)
  } else {
    query = query.or('excerpt.is.null,excerpt.eq.')
  }
  const { data: articles, error: fetchError } = await query

  if (fetchError) {
    return NextResponse.json({ error: fetchError.message }, { status: 500 })
  }

  if (!articles || articles.length === 0) {
    return NextResponse.json({ ok: true, message: 'No articles need meta', updated: 0 })
  }

  const results = []

  for (const article of articles) {
    const message = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      messages: [{
        role: 'user',
        content: `Generate SEO meta tags for this pickleball article.
Title: ${article.title}
Content preview: ${(article.content || '').slice(0, 500)}

Return JSON only:
{
  "meta_title": "SEO title max 60 chars",
  "meta_description": "SEO description max 155 chars",
  "excerpt": "1-2 sentence summary for cards"
}`
      }]
    })

    const text = (message.content[0] as { type: 'text'; text: string }).text
    const parsed = JSON.parse(text.replace(/```json|```/g, '').trim())

    const { error: updateError } = await supabase
      .from('articles')
      .update({
        meta_title: parsed.meta_title,
        meta_description: parsed.meta_description,
        excerpt: parsed.excerpt,
      })
      .eq('id', article.id)

    results.push({
      id: article.id,
      title: article.title,
      success: !updateError,
      error: updateError?.message,
    })
  }

  return NextResponse.json({ ok: true, updated: results.length, results })
}
