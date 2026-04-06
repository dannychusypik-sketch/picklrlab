import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { skillLevel, focusAreas, duration } = body

    if (!skillLevel || !focusAreas || !Array.isArray(focusAreas) || focusAreas.length === 0) {
      return NextResponse.json(
        { error: 'Skill level and at least one focus area are required.' },
        { status: 400 },
      )
    }

    const apiKey = process.env.ANTHROPIC_API_KEY

    if (!apiKey) {
      // Fallback: return a generated template plan when API key is not configured
      const plan = generateFallbackPlan(skillLevel, focusAreas, duration || 30)
      return NextResponse.json({ plan })
    }

    const prompt = `You are a professional pickleball coach. Create a detailed drill plan for a ${skillLevel} player.
Focus areas: ${focusAreas.join(', ')}
Session duration: ${duration || 30} minutes

Format the plan with:
- Warm-up (5 min)
- Main drills (each with name, duration, description, and key coaching points)
- Cool-down (3 min)

Keep it practical and specific to pickleball.`

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        messages: [{ role: 'user', content: prompt }],
      }),
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.error?.message || 'Anthropic API error')
    }

    const data = await response.json()
    const plan = data.content?.[0]?.text || 'Failed to generate plan.'

    return NextResponse.json({ plan })
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : 'Failed to generate drill plan.' },
      { status: 500 },
    )
  }
}

function generateFallbackPlan(skillLevel: string, focusAreas: string[], duration: number): string {
  const warmupTime = 5
  const cooldownTime = 3
  const drillTime = duration - warmupTime - cooldownTime
  const drillMinutes = Math.max(5, Math.floor(drillTime / focusAreas.length))

  let plan = `DRILL PLAN — ${skillLevel}\nDuration: ${duration} minutes\n\n`
  plan += `--- WARM-UP (${warmupTime} min) ---\n`
  plan += `- Light jogging and dynamic stretches\n`
  plan += `- Cross-court dinking rally (2 min)\n`
  plan += `- Progressive drives (2 min)\n\n`

  plan += `--- MAIN DRILLS ---\n\n`

  focusAreas.forEach((area, i) => {
    plan += `Drill ${i + 1}: ${area} Focus (${drillMinutes} min)\n`
    switch (area.toLowerCase()) {
      case 'serves':
        plan += `- Practice deep serves to both corners\n- Focus on consistent toss height\n- Alternate between power and placement\n`
        break
      case 'returns':
        plan += `- Return drills targeting the kitchen line\n- Practice deep returns to push opponent back\n- Work on return footwork\n`
        break
      case 'third shot drop':
        plan += `- Drop shots from baseline to kitchen\n- Partner at net feeding balls\n- Focus on soft hands and arc\n`
        break
      case 'dinking':
        plan += `- Cross-court dinking patterns\n- Dink-and-attack transitions\n- Reset drills from speed-ups\n`
        break
      case 'volleys':
        plan += `- Rapid-fire volley exchanges at the net\n- Practice punch volleys and block volleys\n- Work on reaction time\n`
        break
      case 'drives':
        plan += `- Forehand and backhand drive targets\n- Drive-to-drop transitions\n- Counter-drive rallies\n`
        break
      default:
        plan += `- Progressive ${area.toLowerCase()} drills\n- Focus on technique and consistency\n- Game-situation practice\n`
        break
    }
    plan += `\n`
  })

  plan += `--- COOL-DOWN (${cooldownTime} min) ---\n`
  plan += `- Light rally with focus on placement\n`
  plan += `- Static stretching\n`
  plan += `- Review key takeaways from the session\n`

  return plan
}
