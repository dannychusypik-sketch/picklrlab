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

  const { player_id } = await req.json()

  // Fetch player(s) — single player or all without bio
  let query = supabase.from('players').select('*')
  if (player_id) {
    query = query.eq('id', player_id)
  } else {
    query = query.or('bio.is.null,bio.eq.')
  }
  const { data: players, error: fetchError } = await query

  if (fetchError) {
    return NextResponse.json({ error: fetchError.message }, { status: 500 })
  }

  if (!players || players.length === 0) {
    return NextResponse.json({ ok: true, message: 'No players need bios', updated: 0 })
  }

  const results = []

  for (const player of players) {
    const message = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      messages: [{
        role: 'user',
        content: `Write a ~100 word bio for this pickleball player.
Name: ${player.name}
Country: ${player.country || 'Unknown'}
Ranking: ${player.ranking || 'Unranked'}
Category: ${player.category || 'Unknown'}

Return JSON only:
{
  "bio": "The bio text here"
}`
      }]
    })

    const text = (message.content[0] as { type: 'text'; text: string }).text
    const parsed = JSON.parse(text.replace(/```json|```/g, '').trim())

    const { error: updateError } = await supabase
      .from('players')
      .update({ bio: parsed.bio })
      .eq('id', player.id)

    results.push({
      id: player.id,
      name: player.name,
      success: !updateError,
      error: updateError?.message,
    })
  }

  return NextResponse.json({ ok: true, updated: results.length, results })
}
